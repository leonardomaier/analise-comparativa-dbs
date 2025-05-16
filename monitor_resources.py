import psutil
import time
import subprocess
import csv
import os
import threading
import argparse
import shutil
from dotenv import load_dotenv

load_dotenv(dotenv_path='./env')

def find_main_pid(process_name):
    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cmdline']):
        try:
            if process_name in proc.info['name'] and proc.info['ppid'] == 1:
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_process_tree_cpu_mem(proc):
    try:
        cpu_time = sum([p.cpu_times().user + p.cpu_times().system for p in [proc] + proc.children(recursive=True)])
        mem_percent = sum([p.memory_percent() for p in [proc] + proc.children(recursive=True)])
        return cpu_time, mem_percent
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0, 0.0

def monitor_resources(test_duration, database_to_test, number_of_threads, query_type):
    output_folder_name = './resource-usage'
    resource_usage_file = f'{output_folder_name}/{database_to_test}_{test_duration}_seconds_{number_of_threads}_threads_{query_type}_workload.csv'

    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    process_name = 'postgres' if database_to_test == 'pg' else 'mongod'
    parent_pid = find_main_pid(process_name)
    if not parent_pid:
        print(f"Main process for {process_name} not found.")
        return

    parent_proc = psutil.Process(parent_pid)
    total_cores = psutil.cpu_count(logical=True)

    with open(resource_usage_file, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'CPU Usage', 'Memory Usage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        start_time = time.time()
        last_cpu_time, _ = get_process_tree_cpu_mem(parent_proc)
        last_check_time = time.time()

        while time.time() - start_time < test_duration:
            time.sleep(1)
            current_time = time.time()
            current_cpu_time, mem_percent = get_process_tree_cpu_mem(parent_proc)

            delta_cpu = current_cpu_time - last_cpu_time
            delta_time = current_time - last_check_time

            cpu_percent = (delta_cpu / delta_time) / total_cores * 100.0 if delta_time > 0 else 0.0

            writer.writerow({
                'Time': current_time,
                'CPU Usage': round(cpu_percent, 2),
                'Memory Usage': round(mem_percent, 2)
            })

            last_cpu_time = current_cpu_time
            last_check_time = current_time

def manage_services(database_to_test):
    db_services = {'pg': 'postgresql', 'mongo': 'mongod'}
    active_service = db_services[database_to_test]
    inactive_service = db_services['pg' if database_to_test == 'mongo' else 'mongo']

    subprocess.run(['systemctl', 'stop', inactive_service])
    subprocess.run(['systemctl', 'restart', active_service])
    time.sleep(60)

def start_stress_test(test_duration, number_of_threads, ramp_time, database_to_test, query_type):
    manage_services(database_to_test)

    output_dir = f'./output/{database_to_test}/{test_duration}_seconds_duration/{ramp_time}_seconds_ramp/{number_of_threads}_threads/{query_type}_workload'
    web_dir = f'./web/{database_to_test}/{test_duration}_seconds_duration/{ramp_time}_seconds_ramp/{number_of_threads}_threads/{query_type}_workload'

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists(web_dir):
        shutil.rmtree(web_dir)

    os.makedirs(output_dir)
    os.makedirs(web_dir)

    database_folder_name = "postgres" if database_to_test == "pg" else "mongo"
    jmx_file_path = os.path.expanduser(f'./test-plans/{database_folder_name}/{database_to_test}-{query_type}-workload.jmx')

    monitor_thread = threading.Thread(target=monitor_resources, args=(test_duration, database_to_test, number_of_threads, query_type))
    monitor_thread.start()

    jmeter_command = [
        "jmeter",
        "-n",
        "-t", jmx_file_path,
        "-l", f'{output_dir}/results.csv',
        "-e",
        "-o", web_dir,
        f'-Jduration={test_duration}',
        f'-Jnumber_of_threads={number_of_threads}',
        f'-Jramp_time={ramp_time}'
    ]

    subprocess.run(jmeter_command)
    monitor_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a stress test with specified parameters.")
    parser.add_argument('--duration', type=int, default=30, help="Duration of the test in seconds")
    parser.add_argument('--threads', type=int, default=10, help="Number of threads to simulate in the test")
    parser.add_argument('--ramp', type=int, default=10, help="Ramp up time")
    parser.add_argument('--database', choices=['pg', 'mongo'], default='pg', help="Database to test (pg or mongo)")
    parser.add_argument('--type', choices=['insert', 'update', 'read', 'mixed'], default='insert', help="Type of query to run in the test")

    args = parser.parse_args()
    start_stress_test(args.duration, args.threads, args.ramp, args.database, args.type)
