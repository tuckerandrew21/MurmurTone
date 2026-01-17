"""
Dependency verification for MurmurTone.
Checks that required DLLs are present at startup and offers repair if missing.
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

# Required CUDA DLL files for GPU support
GPU_REQUIRED_DLLS = [
    # cuBLAS
    "cublas64_12.dll",
    "cublasLt64_12.dll",
    # cuDNN
    "cudnn64_9.dll",
    "cudnn_ops64_9.dll",
    "cudnn_cnn64_9.dll",
    "cudnn_adv64_9.dll",
    "cudnn_engines_precompiled64_9.dll",
    "cudnn_engines_runtime_compiled64_9.dll",
    "cudnn_graph64_9.dll",
    "cudnn_heuristic64_9.dll",
]


def get_app_install_dir():
    """Get the application installation directory."""
    if getattr(sys, 'frozen', False):
        # Running as bundled exe - use exe directory
        return os.path.dirname(sys.executable)
    else:
        # Running from source - use script directory
        return os.path.dirname(os.path.abspath(__file__))


def check_gpu_dlls():
    """
    Check if GPU DLLs are present.

    Returns:
        tuple: (all_present: bool, missing: list[str])
    """
    install_dir = get_app_install_dir()
    missing = []

    for dll in GPU_REQUIRED_DLLS:
        dll_path = os.path.join(install_dir, dll)
        if not os.path.exists(dll_path):
            missing.append(dll)

    return len(missing) == 0, missing


def is_gpu_mode_enabled():
    """Check if GPU mode is enabled in config."""
    try:
        import config
        settings = config.load_config()
        processing_mode = settings.get("processing_mode", "auto")
        # GPU mode is enabled if not explicitly set to CPU
        return processing_mode != "cpu"
    except Exception:
        return False


def show_repair_dialog(missing_dlls):
    """
    Show a dialog offering to repair missing dependencies.

    Args:
        missing_dlls: List of missing DLL names

    Returns:
        str: "repair", "continue", or "exit"
    """
    # Create hidden root window
    root = tk.Tk()
    root.withdraw()

    dll_list = "\n".join(f"  - {dll}" for dll in missing_dlls[:5])
    if len(missing_dlls) > 5:
        dll_list += f"\n  ... and {len(missing_dlls) - 5} more"

    message = (
        f"Some GPU libraries are missing:\n\n"
        f"{dll_list}\n\n"
        f"Would you like to:\n"
        f"- Click 'Yes' to download and repair\n"
        f"- Click 'No' to continue without GPU (CPU mode)\n"
        f"- Click 'Cancel' to exit"
    )

    result = messagebox.askyesnocancel(
        "MurmurTone - Missing Dependencies",
        message,
        icon="warning"
    )

    root.destroy()

    if result is True:
        return "repair"
    elif result is False:
        return "continue"
    else:
        return "exit"


def repair_gpu_dependencies():
    """
    Download and install missing GPU dependencies.
    Shows a progress dialog during download.

    Returns:
        bool: True if repair succeeded, False otherwise
    """
    try:
        import requests
        import zipfile
        import tempfile
        import tkinter as tk
        from tkinter import ttk

        # GPU libs download URL (same as in settings_gui.py)
        GPU_LIBS_DOWNLOAD_URL = "https://github.com/tuckerandrew21/MurmurTone/releases/download/gpu-libs-v1.0.0/murmurtone-gpu-libs.zip"

        # Create progress window
        root = tk.Tk()
        root.title("MurmurTone - Repairing Dependencies")
        root.geometry("400x150")
        root.resizable(False, False)

        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 400) // 2
        y = (root.winfo_screenheight() - 150) // 2
        root.geometry(f"+{x}+{y}")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        label = ttk.Label(frame, text="Downloading GPU libraries...")
        label.pack(pady=(0, 10))

        progress = ttk.Progressbar(frame, length=350, mode="determinate")
        progress.pack(pady=5)

        status = ttk.Label(frame, text="Connecting...")
        status.pack(pady=5)

        root.update()

        install_dir = get_app_install_dir()
        temp_zip = None
        success = False

        try:
            # Download
            response = requests.get(GPU_LIBS_DOWNLOAD_URL, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_zip.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        progress['value'] = percent * 0.8  # 80% for download
                        size_mb = downloaded / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        status.config(text=f"Downloading: {size_mb:.1f} / {total_mb:.1f} MB")
                        root.update()

            temp_zip.close()

            # Extract
            status.config(text="Extracting libraries...")
            progress['value'] = 85
            root.update()

            with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
                zip_ref.extractall(install_dir)

            # Verify
            status.config(text="Verifying...")
            progress['value'] = 95
            root.update()

            all_present, missing = check_gpu_dlls()
            if not all_present:
                raise Exception(f"Still missing: {', '.join(missing)}")

            progress['value'] = 100
            status.config(text="Complete!")
            root.update()

            success = True

        except Exception as e:
            messagebox.showerror(
                "Repair Failed",
                f"Failed to download GPU libraries:\n\n{str(e)}\n\n"
                f"You can download manually from:\n"
                f"https://github.com/tuckerandrew21/MurmurTone/releases",
                parent=root
            )

        finally:
            if temp_zip and os.path.exists(temp_zip.name):
                try:
                    os.unlink(temp_zip.name)
                except Exception:
                    pass

            root.after(500 if success else 0, root.destroy)
            if success:
                root.mainloop()

        return success

    except ImportError as e:
        # requests not available - show error
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Repair Unavailable",
            f"Cannot repair dependencies: {str(e)}\n\n"
            f"Please download GPU libraries manually from:\n"
            f"https://github.com/tuckerandrew21/MurmurTone/releases"
        )
        root.destroy()
        return False


def verify_dependencies():
    """
    Main entry point for dependency verification.
    Call this at app startup to check and optionally repair dependencies.

    Returns:
        bool: True if app should continue, False if should exit
    """
    # Only check GPU deps if GPU mode is potentially enabled
    if not is_gpu_mode_enabled():
        return True

    all_present, missing = check_gpu_dlls()

    if all_present:
        return True

    # GPU mode enabled but DLLs missing - ask user
    action = show_repair_dialog(missing)

    if action == "repair":
        if repair_gpu_dependencies():
            return True
        else:
            # Repair failed - ask again
            retry = messagebox.askyesno(
                "Continue Without GPU?",
                "GPU library repair failed.\n\n"
                "Would you like to continue in CPU-only mode?",
            )
            return retry

    elif action == "continue":
        return True

    else:  # exit
        return False


def _auto_check():
    """Auto-check on import (only for bundled exe)."""
    # Only run auto-check for bundled exe, not during development
    if not getattr(sys, 'frozen', False):
        return

    if not verify_dependencies():
        sys.exit(1)


# Auto-check when imported
_auto_check()


if __name__ == "__main__":
    # Test dependency check
    print("Checking GPU dependencies...")
    all_present, missing = check_gpu_dlls()

    if all_present:
        print("All GPU DLLs present!")
    else:
        print(f"Missing DLLs: {missing}")

    print(f"GPU mode enabled: {is_gpu_mode_enabled()}")
