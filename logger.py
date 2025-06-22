import psutil
import pandas as pd
import time
import os

FILE_PATH = "metrics_new.csv"

def get_system_metrics():
    return psutil.cpu_percent(interval=1), psutil.virtual_memory().percent

def get_running_processes():
    process_list = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            cpu_usage = process.info['cpu_percent']
            if cpu_usage >= 1.0:
                priority = process.nice()  # Works across platforms
                process_list.append([
                    process.info['pid'],
                    process.info['name'],
                    cpu_usage,
                    process.info['memory_percent'],
                    priority
                ])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return process_list

def log_metrics():
    columns = ["timestamp", "cpu_usage", "memory_usage", "process_name", "pid", "process_cpu", "process_memory", "process_priority"]
    while True:
        timestamp = int(time.time())
        cpu_usage, memory_usage = get_system_metrics()
        processes = get_running_processes()

        data = [
            [timestamp, cpu_usage, memory_usage, name, pid, cpu, mem, priority]
            for pid, name, cpu, mem, priority in processes
        ]

        df = pd.DataFrame(data, columns=columns)
        df.to_csv(FILE_PATH, mode='a', header=not os.path.exists(FILE_PATH), index=False)
        print(f"📦 Logged {len(data)} processes at {timestamp}")
        time.sleep(5)

if __name__ == "__main__":
    log_metrics()
