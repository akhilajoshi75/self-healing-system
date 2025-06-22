import platform

COOLDOWN_DURATION = 300
def get_excluded_processes():
    os_name = platform.system()
    if os_name == "Windows":
        return {
            "System Idle Process", "System", "Registry", "smss.exe", "csrss.exe",
            "wininit.exe", "winlogon.exe", "services.exe", "lsass.exe", "svchost.exe",
            "explorer.exe", "taskhostw.exe", "spoolsv.exe", "dllhost.exe", "MsMpEng.exe",
            "dwm.exe", "sihost.exe", "OneDrive.exe", "RuntimeBroker.exe", "SearchHost.exe",
            "StartMenuExperienceHost.exe", "MemCompression", "fontdrvhost.exe", "taskmgr.exe"
        }
    elif os_name == "Linux":
        return {"kthreadd", "rcu_sched", "gnome-shell", "systemd", "dbus-daemon"}
    elif os_name == "Darwin":
        return {"kernel_task", "launchd", "WindowServer", "coreaudiod"}
    return set()

KNOWN_APPS = {
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
