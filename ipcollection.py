import pandas as pd
import psutil
import time
import os

FILE_PATH = "metrics.csv"

def get_system_metrics():
    #Fetch system-wide CPU and Memory usage.
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage, memory_usage

def get_running_processes():
    #Fetch active processes with their CPU and Memory usage (Threshold: ≥1% CPU).
    process_list = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        cpu_usage = process.info['cpu_percent']
        if cpu_usage >= 1.0:
            process_list.append([
                process.info['pid'],
                process.info['name'],
                cpu_usage,
                process.info['memory_percent']
            ])
    return process_list

def log_metrics():
    #Log system metrics and running process data to CSV.
    columns = ["timestamp", "cpu_usage", "memory_usage", "process_name", "pid", "process_cpu", "process_memory"]

    while True:
        timestamp = int(time.time())
        cpu_usage, memory_usage = get_system_metrics()
        processes = get_running_processes()

        data = []
        for pid, name, process_cpu, process_mem in processes:
            data.append([timestamp, cpu_usage, memory_usage, name, pid, process_cpu, process_mem])

        df = pd.DataFrame(data, columns=columns)
        df.to_csv(FILE_PATH, mode='a', header=not os.path.exists(FILE_PATH), index=False)

        print(f"Logged {len(data)} processes at {timestamp}")

        time.sleep(5)  
        
if __name__ == "__main__":
    log_metrics()
