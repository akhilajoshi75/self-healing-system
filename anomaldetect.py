import numpy as np
import time
import joblib
import psutil
import subprocess
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load trained model
print("Loading the trained model...")
try:
    model = joblib.load("self_healing_model.pkl")
    logging.info("Model loaded successfully!")
    print("Model loaded successfully!")
except Exception as e:
    logging.error(f"Model loading failed: {e}")
    print(f"Model loading failed: {e}")
    exit(1)

# Cooldown dictionary (stores apps denied for closing with their cooldown expiration time)
cooldown_list = {}

COOLDOWN_DURATION = 300  # 5 minutes (in seconds)

def get_system_metrics():
    """Fetch current system CPU and memory usage."""
    return psutil.cpu_percent(interval=1), psutil.virtual_memory().percent

def get_user_processes():
    """Fetch only user applications, excluding background system processes."""
    
    # Define a list of system processes to exclude
    excluded_processes = {
        "System Idle Process", "System", "Registry", "smss.exe", "csrss.exe",
        "wininit.exe", "winlogon.exe", "services.exe", "lsass.exe", "svchost.exe",
        "explorer.exe", "taskhostw.exe", "spoolsv.exe", "dllhost.exe", "MsMpEng.exe",
        "dwm.exe", "sihost.exe", "OneDrive.exe", "RuntimeBroker.exe", "SearchHost.exe",
        "StartMenuExperienceHost.exe", "MemCompression", "fontdrvhost.exe", "taskmgr.exe"
    }
    known_apps = {
        "Code.exe": "Visual Studio Code",
        "chrome.exe": "Google Chrome",
        "firefox.exe": "Mozilla Firefox",
        "discord.exe": "Discord",
        "notepad.exe": "Notepad",
        "vlc.exe": "VLC Media Player",
        "steam.exe": "Steam",
        "winword.exe": "Microsoft Word",
        "excel.exe": "Microsoft Excel",
        "powerpnt.exe": "Microsoft PowerPoint"
    }

    process_list = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            name = process.info['name']
            cpu_usage = process.info['cpu_percent']

            # Skip system processes and any process with CPU < 1%
            if name in excluded_processes or cpu_usage < 1.0:
                continue
            display_name = known_apps.get(name, name)
            # Ensure process has a visible window (indicating a user application)
            if process.info['pid'] in psutil.pids():
                process_list.append([
                    name,
                    process.info['pid'],
                    cpu_usage,
                    process.info['memory_percent']
                ])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue  # Skip processes that no longer exist

    return process_list

def confirm_and_close(app_name):
    """Show a popup before closing an application. If denied, add to cooldown list."""
    global cooldown_list

    print(f"Alert: Anomaly detected in {app_name}. Requesting user confirmation...")
    
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Force pop-up to appear on top
    root.attributes('-topmost', True)
    root.update()

    user_response = messagebox.askyesno("Self-Healing Alert", f"Anomaly detected in {app_name}. Close it?")

    if user_response:
        close_application(app_name)
    else:
        # Add app to cooldown list with expiration time
        cooldown_list[app_name] = time.time() + COOLDOWN_DURATION
        logging.info(f" {app_name} added to cooldown list until {cooldown_list[app_name]}.")

    root.destroy()


def close_application(app_name):
    """Terminate an application if it's running."""
    try:
        print(f"Closing application: {app_name}...")
        subprocess.run(["taskkill", "/f", "/im", app_name], shell=True, check=True)
        logging.info(f"Successfully closed {app_name}.")
        print(f"Successfully closed {app_name}.")
    except subprocess.CalledProcessError:
        logging.warning(f"Could not close {app_name}. It may not be running.")
        print(f"Could not close {app_name}. It may not be running.")

def monitor_system():
    """Monitor system metrics and detect anomalies in user applications."""
    print("Starting system monitoring... Press CTRL+C to stop.")
    while True:
        cpu_usage, memory_usage = get_system_metrics()
        processes = get_user_processes()

        print(f"Current System Usage -> CPU: {cpu_usage}%, Memory: {memory_usage}%")
        if not processes:
            print("No active user applications consuming significant resources.")
        else:
            print("Scanning user applications...")

        for name, pid, process_cpu, process_mem in processes:
            # Check if app is in cooldown
            if name in cooldown_list and time.time() < cooldown_list[name]:
                logging.info(f"Skipping {name} (in cooldown until {cooldown_list[name]}).")
                continue  # Skip this application

            values = np.array([[cpu_usage, memory_usage, process_cpu, process_mem]])
            prediction = model.predict(values)[0]

            if prediction == -1:
                logging.warning(f"Anomaly detected in {name} (PID: {pid})! Asking for confirmation...")
                print(f"Anomaly detected: {name} (PID: {pid}) - CPU: {process_cpu}%, Memory: {process_mem}%")
                confirm_and_close(name)

        print("Waiting 5 seconds before next scan...\n")
        time.sleep(5)

if __name__ == "__main__":
    monitor_system()
