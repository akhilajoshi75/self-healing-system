import time
import psutil
import joblib
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
import platform
import subprocess
import os
from config import get_excluded_processes, KNOWN_APPS, COOLDOWN_DURATION
import pandas as pd

cooldown_list = {}
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    model = joblib.load("self_healing_model.pkl")
    logging.info("Model loaded successfully!")
except Exception as e:
    logging.error(f"Model load failed: {e}")
    exit(1)

CPU_THRESHOLD = 50.0
MEM_THRESHOLD = 75.0

def load_historical_heavy_apps(csv_file="labeled_metrics.csv"):
    try:
        df = pd.read_csv(csv_file, dtype={"pid": str})
        heavy_apps = df[df['status'] == "High Process Usage"]['process_name'].value_counts()
        return set(heavy_apps[heavy_apps > 3].index.tolist())
    except Exception as e:
        logging.warning(f"Failed to load historical heavy apps: {e}")
        return set()

historical_heavy_apps = load_historical_heavy_apps()

def get_system_metrics():
    return psutil.cpu_percent(interval=1), psutil.virtual_memory().percent

def get_user_processes():
    excluded = get_excluded_processes()
    process_list = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            name = proc.info['name']
            cpu = proc.info['cpu_percent']
            if name in excluded or cpu < 1.0:
                continue
            display_name = KNOWN_APPS.get(name, name)
            process_list.append([display_name, proc.info['pid'], cpu, proc.info['memory_percent'], name])
        except Exception:
            continue
    return process_list

def terminate_process(app_name):
    try:
        for proc in psutil.process_iter(attrs=['name']):
            if proc.info['name'] == app_name:
                proc.terminate()
        logging.info(f"Terminated {app_name}")
    except Exception as e:
        logging.warning(f"Failed to terminate {app_name}: {e}")

def reduce_priority(pid):
    try:
        process = psutil.Process(pid)
        if platform.system() == "Windows":
            process.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            process.nice(19)
        logging.info(f"Reduced priority for PID {pid}")
    except Exception as e:
        logging.warning(f"Failed to reduce priority: {e}")

def clear_cache(app_name):
    try:
        logging.info(f"Cache clear requested for {app_name}, but action is app-specific.")
    except Exception as e:
        logging.warning(f"Failed to clear cache: {e}")

def restart_application(app_name, pid):
    try:
        process = psutil.Process(pid)
        exe_path = process.exe()
        
        exe_dir = os.path.dirname(exe_path)
        exe_name = os.path.basename(exe_path)
        
        process.terminate()
        process.wait(timeout=5)

        if platform.system() == "Windows":
            subprocess.Popen([exe_path], cwd=exe_dir)
            logging.info(f"Restarted application from: {exe_path}")
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            subprocess.Popen([exe_name])  
            logging.info(f"Restarted application from: {exe_name}")
    except Exception as e:
        logging.warning(f"Failed to restart {app_name}: {e}")

def pause_and_resume(pid):
    try:
        process = psutil.Process(pid)
        process.suspend()
        time.sleep(5)
        process.resume()
        logging.info(f"Paused and resumed PID {pid}")
    except Exception as e:
        logging.warning(f"Failed to pause/resume: {e}")

def confirm_and_take_action(app_name, pid, reason="anomaly"):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    if app_name in cooldown_list and time.time() < cooldown_list[app_name]:
        logging.info(f"Skipping action prompt for {app_name} (PID {pid}) due to cooldown.")
        root.destroy()
        return

    if not messagebox.askyesno("Self-Healing System", f"An issue was detected with {app_name}.\nDo you want to take any action?"):
        root.destroy()
        cooldown_list[app_name] = time.time() + COOLDOWN_DURATION
        return

    action = simpledialog.askstring("Healing Action", 
        f"What should I do for {app_name}?\n"
        "1. Terminate Application\n"
        "2. Restart Application\n"
        "3. Reduce Priority\n"
        "4. Pause and Resume\n"
        "5. Cancel\n\nEnter your choice:")

    if action == '1':
        terminate_process(app_name)
    elif action == '2':
        restart_application(app_name, pid)
    elif action == '3':
        reduce_priority(pid)
    elif action == '4':
        pause_and_resume(pid)
    else:
        logging.info(f"No action taken for {app_name}")

    cooldown_list[app_name] = time.time() + COOLDOWN_DURATION
    root.destroy()

def monitor():
    print("Starting system monitoring... Press CTRL+C to stop.\n")
    while True:
        cpu, mem = get_system_metrics()
        print(f"CPU: {cpu:.1f}%, Mem: {mem:.1f}%")

        processes = get_user_processes()
        if not processes:
            print("No active user applications consuming significant resources.")
        else:
            for name, pid, pcpu, pmem, real_name in processes:
                if real_name in cooldown_list and time.time() < cooldown_list[real_name]:
                    continue

                if real_name in historical_heavy_apps:
                    print(f"Historically heavy: {real_name} (PID {pid})")
                    confirm_and_take_action(real_name, pid, reason="historical")
                    continue

                if pcpu >= 5.0 or pmem >= 2.0:
                    values = np.array([[cpu, mem, pcpu, pmem]])
                    try:
                        prediction = model.predict(values)[0]
                        if prediction == -1:
                            print(f"Anomaly detected: {real_name} (PID {pid})")
                            confirm_and_take_action(real_name, pid, reason="anomaly")
                            continue
                    except Exception as e:
                        logging.warning(f"Model prediction failed: {e}")

                if pcpu >= CPU_THRESHOLD or pmem >= MEM_THRESHOLD:
                    print(f"High usage: {real_name} (PID {pid}) CPU: {pcpu:.1f}%, Mem: {pmem:.1f}%")
                    confirm_and_take_action(real_name, pid, reason="heavy")

        
        time.sleep(5)

if __name__ == "__main__":
    monitor()
