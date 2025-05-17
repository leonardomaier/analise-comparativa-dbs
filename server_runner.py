import psutil
import time
import csv
import os
import argparse
from dotenv import load_dotenv

load_dotenv(dotenv_path='./env')

def monitor_resources(test_duration, number_of_threads, database_to_test, query_type):
    output_folder_name = './resource-usage'
    resource_usage_file = f'{output_folder_name}/{database_to_test}_{test_duration}_seconds_{number_of_threads}_threads_{query_type}_workload.csv'

    if not os.path.exists(f'{output_folder_name}/'):
        os.makedirs(f'{output_folder_name}/')

    with open(resource_usage_file, 'w', newline='') as csvfile:
        fieldnames = ['Time', 'CPU Usage', 'Memory Usage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        start_time = time.time()

        while time.time() - start_time < test_duration:
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()

            writer.writerow({
                'Time': time.time(),
                'CPU Usage': cpu_usage,
                'Memory Usage': memory_info.percent
            })
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor system resources")
    parser.add_argument('--duration', type=int, required=True)
    parser.add_argument('--threads', type=int, required=True)
    parser.add_argument('--ramp', type=int, required=True)
    parser.add_argument('--database', choices=['pg', 'mongo'], required=True)
    parser.add_argument('--type', choices=['insert', 'update', 'read', 'mixed'], required=True)

    args = parser.parse_args()
    monitor_resources(args.duration, args.threads, args.database, args.type)
