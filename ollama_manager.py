"""
Manage bundled Ollama subprocess lifecycle.

Starts Ollama as a hidden subprocess when MurmurTone launches,
and ensures it terminates when the app closes (even on crash).
"""
import subprocess
import atexit
import os
import sys
import time
import ctypes
from ctypes import wintypes
from typing import Optional
import requests


# Windows Job Object constants for killing child processes on parent exit
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JobObjectExtendedLimitInformation = 9

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('PerProcessUserTimeLimit', ctypes.c_int64),
        ('PerJobUserTimeLimit', ctypes.c_int64),
        ('LimitFlags', wintypes.DWORD),
        ('MinimumWorkingSetSize', ctypes.c_size_t),
        ('MaximumWorkingSetSize', ctypes.c_size_t),
        ('ActiveProcessLimit', wintypes.DWORD),
        ('Affinity', ctypes.POINTER(ctypes.c_ulong)),
        ('PriorityClass', wintypes.DWORD),
        ('SchedulingClass', wintypes.DWORD),
    ]

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ('ReadOperationCount', ctypes.c_uint64),
        ('WriteOperationCount', ctypes.c_uint64),
        ('OtherOperationCount', ctypes.c_uint64),
        ('ReadTransferCount', ctypes.c_uint64),
        ('WriteTransferCount', ctypes.c_uint64),
        ('OtherTransferCount', ctypes.c_uint64),
    ]

class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ('IoInfo', IO_COUNTERS),
        ('ProcessMemoryLimit', ctypes.c_size_t),
        ('JobMemoryLimit', ctypes.c_size_t),
        ('PeakProcessMemoryUsed', ctypes.c_size_t),
        ('PeakJobMemoryUsed', ctypes.c_size_t),
    ]


_ollama_process: Optional[subprocess.Popen] = None
_job_handle = None


def get_ollama_path() -> str:
    """Get path to bundled ollama.exe."""
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        base = sys._MEIPASS
    else:
        # Development - look for ollama folder next to this file
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "ollama", "ollama.exe")


def get_models_path() -> str:
    """Get custom models directory in AppData."""
    appdata = os.environ.get('APPDATA', '')
    if not appdata:
        appdata = os.path.expanduser('~')
    models_dir = os.path.join(appdata, 'MurmurTone', 'models')
    os.makedirs(models_dir, exist_ok=True)
    return models_dir


def _create_job_object():
    """Create a Windows Job Object that kills children when parent dies."""
    global _job_handle

    kernel32 = ctypes.windll.kernel32

    # Create job object
    _job_handle = kernel32.CreateJobObjectW(None, None)
    if not _job_handle:
        return False

    # Configure to kill on close
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

    result = kernel32.SetInformationJobObject(
        _job_handle,
        JobObjectExtendedLimitInformation,
        ctypes.byref(info),
        ctypes.sizeof(info)
    )

    return bool(result)


def _assign_process_to_job(process_handle):
    """Assign a process to the job object."""
    global _job_handle
    if _job_handle:
        kernel32 = ctypes.windll.kernel32
        return kernel32.AssignProcessToJobObject(_job_handle, process_handle)
    return False


def is_ollama_running() -> bool:
    """Check if Ollama API is responding."""
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def start_ollama() -> bool:
    """
    Start Ollama subprocess if not running.

    Returns:
        True if Ollama is running (either started or already was), False on failure.
    """
    global _ollama_process

    # If Ollama is already running (maybe user has it installed), use it
    if is_ollama_running():
        return True

    ollama_exe = get_ollama_path()
    if not os.path.exists(ollama_exe):
        print(f"[ollama_manager] ollama.exe not found at: {ollama_exe}")
        return False

    # Create job object for crash protection
    _create_job_object()

    # Set up environment
    env = os.environ.copy()
    env['OLLAMA_MODELS'] = get_models_path()
    env['OLLAMA_HOST'] = '127.0.0.1:11434'
    # Disable Ollama's auto-update check
    env['OLLAMA_NOPRUNE'] = '1'

    try:
        # Start Ollama as hidden subprocess
        _ollama_process = subprocess.Popen(
            [ollama_exe, "serve"],
            env=env,
            cwd=os.path.dirname(ollama_exe),  # Run from ollama dir for DLL loading
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Assign to job object so it dies if we crash
        if _job_handle and _ollama_process:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x1F0FFF, False, _ollama_process.pid)  # PROCESS_ALL_ACCESS
            if handle:
                _assign_process_to_job(handle)
                kernel32.CloseHandle(handle)

        # Register cleanup for normal exit
        atexit.register(stop_ollama)

        # Wait for Ollama to be ready (max 15s - first start can be slow)
        for i in range(30):
            if is_ollama_running():
                print(f"[ollama_manager] Ollama started successfully (took {(i+1)*0.5:.1f}s)")
                return True
            time.sleep(0.5)

        print("[ollama_manager] Ollama failed to respond within 15s")
        return False

    except Exception as e:
        print(f"[ollama_manager] Failed to start Ollama: {e}")
        return False


def stop_ollama():
    """Stop Ollama subprocess."""
    global _ollama_process, _job_handle

    if _ollama_process:
        try:
            _ollama_process.terminate()
            _ollama_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _ollama_process.kill()
        except Exception:
            pass
        _ollama_process = None
        print("[ollama_manager] Ollama stopped")

    # Clean up job object
    if _job_handle:
        ctypes.windll.kernel32.CloseHandle(_job_handle)
        _job_handle = None


def get_ollama_status() -> dict:
    """
    Get current Ollama status.

    Returns:
        dict with 'running', 'bundled', 'models_path' keys
    """
    return {
        'running': is_ollama_running(),
        'bundled': os.path.exists(get_ollama_path()),
        'models_path': get_models_path(),
        'ollama_path': get_ollama_path(),
    }


if __name__ == "__main__":
    # Test the manager
    print("Ollama status:", get_ollama_status())
    print("Starting Ollama...")
    if start_ollama():
        print("Ollama is running!")
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start Ollama")
    stop_ollama()
