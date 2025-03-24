import psutil
import time
import subprocess
import csv
import os
import threading
import argparse
import shutil

def monitor_resources(test_duration):
    with open('metrics_during_stress_test.csv', 'w', newline='') as csvfile:
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

    # Clean up the "web" and "output" folders before running JMeter
    output_dir = './web'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Removes the directory and all its contents

    # Clean up the output directory
    result_output_dir = './output'
    if os.path.exists(result_output_dir):
        shutil.rmtree(result_output_dir)  # Removes the directory and all its contents

    # Recreate the folders to avoid errors (JMeter expects them to exist)
    # os.makedirs(output_dir)
    # os.makedirs(result_output_dir)

    # Recreate the folder to avoid errors (JMeter expects it to exist)
    os.makedirs(output_dir)

    jmx_file_path = os.path.expanduser(f'~/Documents/TCC/analise-comparativa-dbs/test-plans/postgres/{database_to_test}-{query_type}-workload.jmx')
    
    monitor_thread = threading.Thread(target=monitor_resources, args=(test_duration,))
    monitor_thread.start()
    
    jmeter_command = [
        "jmeter", 
        "-n", 
        "-t", 
        jmx_file_path, 
        "-l", 
        "./output/results.csv", 
        "-e", 
        "-o", 
        "./web", 
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
