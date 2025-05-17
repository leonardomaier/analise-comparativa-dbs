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

def monitor_resources(test_duration, database_to_test, number_of_threads, query_type):
    output_folder_name = './resource-usage'
    resource_usage_file = f'{output_folder_name}/{database_to_test}_{test_duration}_seconds_{number_of_threads}_threads_{query_type}_workload.csv'

    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    process_name = 'postgres' if database_to_test == 'pg' else 'mongod'
    pid = find_main_pid(process_name)
    if not pid:
        print(f"Processo principal de {process_name} não encontrado.")
        return

    proc = psutil.Process(pid)
    with open(resource_usage_file, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'CPU Usage', 'Memory Usage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        start_time = time.time()
        while time.time() - start_time < test_duration:
            try:
                cpu = proc.cpu_percent(interval=1)
                mem_percent = proc.memory_percent()  # Memory usage in percentage
                writer.writerow({
                    'Time': time.time(),
                    'CPU Usage': cpu,
                    'Memory Usage': mem_percent
                })
            except psutil.NoSuchProcess:
                break


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