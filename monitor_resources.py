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

def monitor_resources(test_duration, number_of_threads, database_to_test, query_type):
    with open(f'{database_to_test}_{test_duration}_seconds_{number_of_threads}_threads_{query_type}_workload.csv', 'w', newline='') as csvfile:
        fieldnames = ['Time', 'CPU Usage', 'Memory Usage', 'Disk Read', 'Disk Write', 'Network Sent', 'Network Recv', 'IOPS Read', 'IOPS Write']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        prev_disk_io = psutil.disk_io_counters()

        start_time = time.time()

        while time.time() - start_time < test_duration:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_io_counters()
            network_info = psutil.net_io_counters()

            read_iops = disk_info.read_count - prev_disk_io.read_count
            write_iops = disk_info.write_count - prev_disk_io.write_count
            writer.writerow({
                'Time': time.time(),
                'CPU Usage': cpu_usage,
                'Memory Usage': memory_info.percent,
                'Disk Read': disk_info.read_bytes,
                'Disk Write': disk_info.write_bytes,
                'Network Sent': network_info.bytes_sent,
                'Network Recv': network_info.bytes_recv,
                'IOPS Read': read_iops,
                'IOPS Write': write_iops
            })

            # Update previous disk I/O counters for the next iteration
            prev_disk_io = disk_info
            
            time.sleep(1)  # Sleep for 1 second before recording again

# Start the stress test and monitor resources simultaneously
def start_stress_test(test_duration, number_of_threads, database_to_test, query_type):

    output_dir = f'./output/{database_to_test}/{test_duration}_seconds/{number_of_threads}_threads/{query_type}_workload'
    web_dir = f'./web/{database_to_test}/{test_duration}_seconds/{number_of_threads}_threads/{query_type}_workload'

    # Clean up the "web" and "output" folders before running JMeter
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Removes the directory and all its contents

    # Clean up the output directory
    if os.path.exists(web_dir):
        shutil.rmtree(web_dir)  # Removes the directory and all its contents

    # Recreate the folders to avoid errors (JMeter expects them to exist)
    os.makedirs(output_dir)
    os.makedirs(web_dir)

    database_folder_name = "postgres" if database_to_test == "pg" else "mongo"

    jmx_file_path = os.path.expanduser(f'{os.getenv("REPOSITORY_PATH")}/test-plans/{database_folder_name}/{database_to_test}-{query_type}-workload.jmx')
    
    monitor_thread = threading.Thread(target=monitor_resources, args=(test_duration, number_of_threads, database_to_test, query_type))
    monitor_thread.start()
    
    jmeter_command = [
        "jmeter", 
        "-n", 
        "-t", 
        jmx_file_path, 
        "-l", 
        f'{output_dir}/results.csv', 
        "-e", 
        "-o", 
        web_dir, 
        f'-Jduration={test_duration}',
        f'-Jnumber_of_threads={number_of_threads}',
    ]
    
    subprocess.run(jmeter_command)

    # After the stress test is completed, stop the monitoring
    monitor_thread.join()

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a stress test with specified parameters.")
    parser.add_argument('--duration', type=int, default=30, help="Duration of the test in seconds")
    parser.add_argument('--threads', type=int, default=10, help="Number of threads to simulate in the test")
    parser.add_argument('--database', choices=['pg', 'mongo'], default='pg', help="Database to test (pg or mongo)")
    parser.add_argument('--type', choices=['insert', 'update', 'read', 'mixed'], default='insert', help="Type of query to run in the test")

    args = parser.parse_args()

    start_stress_test(args.duration, args.threads, args.database, args.type)
