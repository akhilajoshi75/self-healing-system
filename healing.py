import time
import psutil
import joblib
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
import platform
import subprocess
import pandas as pd
from config import get_excluded_processes, KNOWN_APPS, COOLDOWN_DURATION

cooldown_list = {}
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    model = joblib.load("self_healing_model_new.pkl")
    logging.info("Model loaded successfully!")
except Exception as e:
    logging.error(f"Model load failed: {e}")
    exit(1)

# Thresholds for heavy app usage (adjust as needed)
CPU_THRESHOLD = 50.0  # %
MEM_THRESHOLD = 20.0  # %

def load_historical_heavy_apps(csv_file="labeled_metrics_new.csv"):
    try:
        df = pd.read_csv(csv_file)
        heavy_apps = df[df['status'] == "High Process Usage"]['process_name'].value_counts()
        return set(heavy_apps[heavy_apps > 3].index.tolist())  # apps that frequently crossed threshold
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
            process_list.append([display_name, proc.info['pid'], cpu, proc.info['memory_percent']])
        except Exception:
            continue
    return process_list

def terminate_process(app_name):
    os_name = platform.system()
    try:
        if os_name == "Windows":
            subprocess.run(["taskkill", "/f", "/im", app_name], check=True, shell=True)
        elif os_name == "Linux":
            subprocess.run(["pkill", "-f", app_name], check=True)
        elif os_name == "Darwin":
            subprocess.run(["osascript", "-e", f'tell application \"{app_name}\" to quit'], check=True)
        logging.info(f"Terminated {app_name}")
    except Exception as e:
        logging.warning(f"Failed to terminate {app_name}: {e}")

def offer_alternative(app_name, processes):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    alternatives = [f"{name} (PID: {pid}) - CPU: {cpu:.1f}%" for name, pid, cpu, mem in processes if name != app_name]
    if not alternatives:
        messagebox.showinfo("No Alternatives", "No other significant apps to close.")
        return

    selected = simpledialog.askstring("Alternative Option", 
        f"{app_name} is using high resources.\nChoose an alternative app to close:\n\n" +
        "\n".join(f"{i+1}. {alt}" for i, alt in enumerate(alternatives)) + 
        "\n\nEnter the number or click Cancel to skip.")

    if selected and selected.isdigit():
        idx = int(selected) - 1
        if 0 <= idx < len(alternatives):
            alt_app_info = alternatives[idx]
            alt_name = alt_app_info.split(" (PID")[0]
            terminate_process(alt_name)
            logging.info(f"User chose to close alternative: {alt_name}")
    root.destroy()

def confirm_and_close(app_name, processes, reason="anomaly"):
    global cooldown_list
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    if reason == "anomaly":
        message = f"{app_name} is behaving abnormally.\nDo you want to close it?"
    elif reason == "heavy":
        message = f"{app_name} is consuming high resources.\nDo you want to close it?"
    elif reason == "historical":
        message = f"{app_name} is known to consume heavy resources frequently.\nDo you want to close it?"

    user_choice = messagebox.askyesno("Self-Healing Alert", message)
    root.destroy()

    if user_choice:
        terminate_process(app_name)
    else:
        offer_alternative(app_name, processes)
        cooldown_list[app_name] = time.time() + COOLDOWN_DURATION

def monitor():
    print("🛡️ Starting system monitoring... Press CTRL+C to stop.\n")
    while True:
        cpu, mem = get_system_metrics()
        print(f"🖥️ Current System Usage -> CPU: {cpu:.1f}%, Memory: {mem:.1f}%")

        processes = get_user_processes()
        if not processes:
            print("ℹ️ No active user applications consuming significant resources.")
        else:
            print("🔍 Scanning user applications...")
            for name, pid, pcpu, pmem in processes:
                if name in cooldown_list and time.time() < cooldown_list[name]:
                    remaining = int(cooldown_list[name] - time.time())
                    print(f"⏳ Skipping {name} (PID: {pid}) - In cooldown for {remaining}s")
                    continue

                # Historical heavy app check
                if name in historical_heavy_apps:
                    print(f"📊 Historically heavy app detected: {name} (PID: {pid})")
                    confirm_and_close(name, processes, reason="historical")
                    continue

                # Model-based anomaly detection
                values = np.array([[cpu, mem, pcpu, pmem]])
                prediction = model.predict(values)[0]
                if prediction == -1:
                    print(f"⚠️ Anomaly detected: {name} (PID: {pid})")
                    confirm_and_close(name, processes, reason="anomaly")
                    continue

                # Threshold-based heavy app detection
                if pcpu >= CPU_THRESHOLD or pmem >= MEM_THRESHOLD:
                    print(f"💡 High resource usage: {name} (PID: {pid}) - CPU: {pcpu:.1f}%, Mem: {pmem:.1f}%")
                    confirm_and_close(name, processes, reason="heavy")

                else:
                    print(f"✅ {name} (PID: {pid}) is operating normally.")

        print("⏱️ Waiting 5 seconds before next scan...\n")
        time.sleep(5)

if __name__ == "__main__":
    monitor()