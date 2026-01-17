"""
Dependency verification for MurmurTone.
Checks that required DLLs are present at startup and offers repair if missing.
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

try:
    import customtkinter as ctk
    from theme import (
        PRIMARY, PRIMARY_DARK, SLATE_100, SLATE_200, SLATE_400,
        SLATE_500, SLATE_600, SLATE_700, SLATE_800, SLATE_900
    )
    HAS_CTK = True
except ImportError:
    HAS_CTK = False

# Font and spacing constants (fallback if theme not available)
FONT_FAMILY = "Roboto Serif"
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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


# =============================================================================
# MODEL DEPENDENCY CHECKING
# =============================================================================


def get_models_dir():
    """Get the models directory path."""
    install_dir = get_app_install_dir()
    return os.path.join(install_dir, "models")


def check_model_available(model_name):
    """
    Check if a Whisper model is available locally.

    Checks both bundled models directory and HuggingFace cache.

    Args:
        model_name: Name of the model (e.g., "tiny", "small")

    Returns:
        tuple: (is_available: bool, path_or_none: str|None)
    """
    # Check bundled models first
    models_dir = get_models_dir()
    bundled_path = os.path.join(models_dir, model_name)
    if os.path.isdir(bundled_path):
        # Verify it has model files
        if os.path.exists(os.path.join(bundled_path, "model.bin")):
            return True, bundled_path

    # Check HuggingFace cache
    try:
        from pathlib import Path
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        if cache_dir.exists():
            pattern = f"models--Systran--faster-whisper-{model_name}"
            for item in cache_dir.iterdir():
                if item.is_dir() and item.name.startswith(pattern):
                    snapshots_dir = item / "snapshots"
                    if snapshots_dir.exists():
                        snapshots = list(snapshots_dir.iterdir())
                        if snapshots:
                            return True, str(snapshots[0])
    except Exception:
        pass

    return False, None


def get_selected_model():
    """Get the currently selected model from config."""
    try:
        import config
        settings = config.load_config()
        return settings.get("model_size", "tiny")
    except Exception:
        return "tiny"


def show_model_download_dialog(model_name):
    """
    Show a branded dialog when a model is not available.

    Args:
        model_name: Name of the missing model

    Returns:
        str: "download", "fallback", or "exit"
    """
    try:
        from config import MODEL_SIZES_MB, BUNDLED_MODELS
        size_mb = MODEL_SIZES_MB.get(model_name, 500)
        fallback_model = BUNDLED_MODELS[0] if BUNDLED_MODELS else "tiny"
    except ImportError:
        size_mb = 500
        fallback_model = "tiny"

    # Fallback to plain messagebox if customtkinter not available
    if not HAS_CTK:
        root = tk.Tk()
        root.withdraw()
        message = (
            f"The {model_name} model is not installed.\n\n"
            f"Download size: ~{size_mb} MB\n\n"
            f"Would you like to:\n"
            f"- Click 'Yes' to download the model\n"
            f"- Click 'No' to use {fallback_model} instead\n"
            f"- Click 'Cancel' to exit"
        )
        result = messagebox.askyesnocancel(
            "MurmurTone - Model Not Found", message, icon="question"
        )
        root.destroy()
        if result is True:
            return "download"
        elif result is False:
            return "fallback"
        return "exit"

    # Branded CTk dialog
    result = {"action": "exit"}

    dialog = ctk.CTk()
    dialog.title("MurmurTone - Model Not Found")
    dialog.geometry("420x220")
    dialog.resizable(False, False)
    dialog.configure(fg_color=SLATE_800)

    # Center on screen
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 420) // 2
    y = (dialog.winfo_screenheight() - 220) // 2
    dialog.geometry(f"+{x}+{y}")

    # Set window icon
    try:
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            dialog.after(200, lambda: dialog.iconbitmap(icon_path))
    except Exception:
        pass

    frame = ctk.CTkFrame(dialog, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=SPACE_LG, pady=SPACE_LG)

    # Title
    ctk.CTkLabel(
        frame,
        text=f"Download {model_name} Model?",
        font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
        text_color=SLATE_100,
    ).pack(pady=(SPACE_MD, SPACE_SM))

    # Info text
    ctk.CTkLabel(
        frame,
        text=f"The {model_name} model is not installed.\nDownload size: ~{size_mb} MB",
        font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        text_color=SLATE_400,
        justify="center",
    ).pack(pady=(0, SPACE_LG))

    # Buttons
    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(SPACE_SM, 0))

    def on_download():
        result["action"] = "download"
        dialog.destroy()

    def on_fallback():
        result["action"] = "fallback"
        dialog.destroy()

    def on_exit():
        result["action"] = "exit"
        dialog.destroy()

    ctk.CTkButton(
        btn_frame,
        text="Download",
        command=on_download,
        font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        fg_color=PRIMARY,
        hover_color=PRIMARY_DARK,
        width=110,
        height=36,
    ).pack(side="left", expand=True, padx=4)

    ctk.CTkButton(
        btn_frame,
        text=f"Use {fallback_model}",
        command=on_fallback,
        font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        fg_color=SLATE_700,
        hover_color=SLATE_600,
        width=110,
        height=36,
    ).pack(side="left", expand=True, padx=4)

    ctk.CTkButton(
        btn_frame,
        text="Exit",
        command=on_exit,
        font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        fg_color=SLATE_700,
        hover_color=SLATE_600,
        width=80,
        height=36,
    ).pack(side="left", expand=True, padx=4)

    dialog.mainloop()
    return result["action"]


def download_model(model_name):
    """
    Download a model with branded progress UI.

    Args:
        model_name: Name of the model to download

    Returns:
        bool: True if download succeeded, False otherwise
    """
    # Check if this model downloads from HuggingFace instead of GitHub
    try:
        from config import HUGGINGFACE_MODELS
        if model_name in HUGGINGFACE_MODELS:
            return _download_model_huggingface(model_name)
    except ImportError:
        pass

    try:
        import requests
        import zipfile
        import tempfile
        from config import MODEL_DOWNLOAD_URLS, MODEL_SIZES_MB
    except ImportError as e:
        _show_error_dialog(
            "Download Unavailable",
            f"Cannot download model: {str(e)}\n\n"
            f"Please download manually from:\n"
            f"https://github.com/tuckerandrew21/MurmurTone/releases"
        )
        return False

    download_url = MODEL_DOWNLOAD_URLS.get(model_name)
    if not download_url:
        _show_error_dialog(
            "Download Error",
            f"No download URL configured for model: {model_name}"
        )
        return False

    # Use branded CTk dialog if available, else fallback to ttk
    if not HAS_CTK:
        return _download_model_ttk(model_name, download_url)

    # Create branded progress window
    dialog = ctk.CTk()
    dialog.title(f"MurmurTone - Downloading {model_name}")
    dialog.geometry("420x180")
    dialog.resizable(False, False)
    dialog.configure(fg_color=SLATE_800)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent close during download

    # Center on screen
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 420) // 2
    y = (dialog.winfo_screenheight() - 180) // 2
    dialog.geometry(f"+{x}+{y}")

    # Set window icon
    try:
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            dialog.after(200, lambda: dialog.iconbitmap(icon_path))
    except Exception:
        pass

    frame = ctk.CTkFrame(dialog, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=SPACE_LG, pady=SPACE_LG)

    # Title
    ctk.CTkLabel(
        frame,
        text=f"Downloading {model_name} Model",
        font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
        text_color=SLATE_100,
    ).pack(pady=(SPACE_SM, SPACE_MD))

    # Progress bar
    progress = ctk.CTkProgressBar(frame, width=380, mode="determinate")
    progress.pack(pady=SPACE_SM)
    progress.set(0)

    # Status label
    status_label = ctk.CTkLabel(
        frame,
        text="Connecting...",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        text_color=SLATE_400,
    )
    status_label.pack(pady=SPACE_SM)

    dialog.update()

    models_dir = get_models_dir()
    temp_zip = None
    success = False

    try:
        # Download
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_zip.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = downloaded / total_size
                    progress.set(percent * 0.8)  # 80% for download
                    size_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    status_label.configure(text=f"Downloading: {size_mb:.1f} / {total_mb:.1f} MB")
                    dialog.update()

        temp_zip.close()

        # Extract
        status_label.configure(text="Extracting model...")
        progress.set(0.85)
        dialog.update()

        os.makedirs(models_dir, exist_ok=True)

        with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
            zip_ref.extractall(models_dir)

        # Verify
        status_label.configure(text="Verifying...")
        progress.set(0.95)
        dialog.update()

        is_available, _ = check_model_available(model_name)
        if not is_available:
            raise Exception("Model extraction failed - files not found")

        progress.set(1.0)
        status_label.configure(text="Complete!")
        dialog.update()

        success = True

    except Exception as e:
        error_msg = str(e)
        # Destroy progress dialog before showing error
        dialog.destroy()
        _show_error_dialog(
            "Download Failed",
            f"Failed to download model:\n\n{error_msg}\n\n"
            f"You can download manually from:\n"
            f"https://github.com/tuckerandrew21/MurmurTone/releases"
        )

    else:
        # Only run mainloop on success path
        dialog.after(500, dialog.destroy)
        dialog.mainloop()

    finally:
        if temp_zip and os.path.exists(temp_zip.name):
            try:
                os.unlink(temp_zip.name)
            except Exception:
                pass

    return success


def _show_error_dialog(title, message):
    """Show a branded error dialog."""
    if not HAS_CTK:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
        return

    dialog = ctk.CTk()
    dialog.title(title)
    dialog.geometry("420x200")
    dialog.resizable(False, False)
    dialog.configure(fg_color=SLATE_800)

    # Center on screen
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 420) // 2
    y = (dialog.winfo_screenheight() - 200) // 2
    dialog.geometry(f"+{x}+{y}")

    # Set window icon
    try:
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            dialog.after(200, lambda: dialog.iconbitmap(icon_path))
    except Exception:
        pass

    frame = ctk.CTkFrame(dialog, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=SPACE_LG, pady=SPACE_LG)

    ctk.CTkLabel(
        frame,
        text=title,
        font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
        text_color=SLATE_100,
    ).pack(pady=(0, SPACE_SM))

    ctk.CTkLabel(
        frame,
        text=message,
        font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        text_color=SLATE_400,
        wraplength=380,
        justify="center",
    ).pack(pady=(0, SPACE_LG))

    ctk.CTkButton(
        frame,
        text="OK",
        command=dialog.destroy,
        font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        fg_color=PRIMARY,
        hover_color=PRIMARY_DARK,
        width=100,
        height=36,
    ).pack()

    dialog.mainloop()


def _download_model_huggingface(model_name):
    """
    Download a model directly from HuggingFace using faster-whisper.

    Used for models too large for GitHub releases (e.g., large-v3).

    Args:
        model_name: Name of the model to download

    Returns:
        bool: True if download succeeded, False otherwise
    """
    try:
        from config import MODEL_SIZES_MB
        size_mb = MODEL_SIZES_MB.get(model_name, 3000)
    except ImportError:
        size_mb = 3000

    # Show a simple info dialog since we can't show progress for HF downloads
    if HAS_CTK:
        dialog = ctk.CTk()
        dialog.title(f"MurmurTone - Downloading {model_name}")
        dialog.geometry("420x160")
        dialog.resizable(False, False)
        dialog.configure(fg_color=SLATE_800)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 420) // 2
        y = (dialog.winfo_screenheight() - 160) // 2
        dialog.geometry(f"+{x}+{y}")

        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                dialog.after(200, lambda: dialog.iconbitmap(icon_path))
        except Exception:
            pass

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=SPACE_LG, pady=SPACE_LG)

        ctk.CTkLabel(
            frame,
            text=f"Downloading {model_name} Model",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=SLATE_100,
        ).pack(pady=(SPACE_SM, SPACE_MD))

        ctk.CTkLabel(
            frame,
            text=f"Downloading ~{size_mb} MB from HuggingFace...\nThis may take several minutes.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=SLATE_400,
            justify="center",
        ).pack(pady=SPACE_SM)

        progress = ctk.CTkProgressBar(frame, width=380, mode="indeterminate")
        progress.pack(pady=SPACE_SM)
        progress.start()

        dialog.update()
    else:
        dialog = None

    try:
        # Use faster-whisper to download the model
        from faster_whisper import WhisperModel
        _ = WhisperModel(model_name, device="cpu", compute_type="int8")

        # Verify it's available now
        is_available, _ = check_model_available(model_name)
        if not is_available:
            raise Exception("Model download completed but files not found")

        if dialog:
            dialog.destroy()
        return True

    except Exception as e:
        if dialog:
            dialog.destroy()
        _show_error_dialog(
            "Download Failed",
            f"Failed to download model from HuggingFace:\n\n{str(e)}"
        )
        return False


def _download_model_ttk(model_name, download_url):
    """Fallback download with ttk progress bar (when CTk not available)."""
    import requests
    import zipfile
    import tempfile
    from tkinter import ttk

    root = tk.Tk()
    root.title(f"MurmurTone - Downloading {model_name}")
    root.geometry("400x150")
    root.resizable(False, False)

    root.update_idletasks()
    x = (root.winfo_screenwidth() - 400) // 2
    y = (root.winfo_screenheight() - 150) // 2
    root.geometry(f"+{x}+{y}")

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    label = ttk.Label(frame, text=f"Downloading {model_name} model...")
    label.pack(pady=(0, 10))

    progress = ttk.Progressbar(frame, length=350, mode="determinate")
    progress.pack(pady=5)

    status = ttk.Label(frame, text="Connecting...")
    status.pack(pady=5)

    root.update()

    models_dir = get_models_dir()
    temp_zip = None
    success = False

    try:
        response = requests.get(download_url, stream=True, timeout=30)
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
                    progress['value'] = percent * 0.8
                    size_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    status.config(text=f"Downloading: {size_mb:.1f} / {total_mb:.1f} MB")
                    root.update()

        temp_zip.close()

        status.config(text="Extracting model...")
        progress['value'] = 85
        root.update()

        os.makedirs(models_dir, exist_ok=True)

        with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
            zip_ref.extractall(models_dir)

        status.config(text="Verifying...")
        progress['value'] = 95
        root.update()

        is_available, _ = check_model_available(model_name)
        if not is_available:
            raise Exception("Model extraction failed - files not found")

        progress['value'] = 100
        status.config(text="Complete!")
        root.update()

        success = True

    except Exception as e:
        messagebox.showerror(
            "Download Failed",
            f"Failed to download model:\n\n{str(e)}\n\n"
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


def set_fallback_model(fallback_model="base"):
    """Update config to use the fallback model."""
    try:
        import config
        settings = config.load_config()
        settings["model_size"] = fallback_model
        config.save_config(settings)
        return True
    except Exception:
        return False


def verify_model_dependencies():
    """
    Check if the selected model is available.
    Called at app startup.

    Returns:
        bool: True if app should continue, False if should exit
    """
    model_name = get_selected_model()
    is_available, _ = check_model_available(model_name)

    if is_available:
        return True

    # Model not available - check if it's a downloadable model
    try:
        from config import BUNDLED_MODELS, DOWNLOADABLE_MODELS
    except ImportError:
        BUNDLED_MODELS = ["tiny", "base"]
        DOWNLOADABLE_MODELS = ["small", "medium", "large-v3"]

    if model_name in BUNDLED_MODELS:
        # Bundled model should always be present - this is an error
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "MurmurTone - Installation Error",
            f"The bundled model '{model_name}' is missing.\n\n"
            f"This indicates a corrupted installation.\n"
            f"Please reinstall MurmurTone."
        )
        root.destroy()
        return False

    # Downloadable model - offer to download
    action = show_model_download_dialog(model_name)

    if action == "download":
        if download_model(model_name):
            return True
        else:
            # Download failed - offer fallback
            retry = messagebox.askyesno(
                "Use Default Model?",
                f"Model download failed.\n\n"
                f"Would you like to use the default model instead?",
            )
            if retry:
                set_fallback_model()
                return True
            return False

    elif action == "fallback":
        set_fallback_model()
        return True

    else:  # exit
        return False


# =============================================================================
# MAIN VERIFICATION ENTRY POINT
# =============================================================================


def verify_dependencies():
    """
    Main entry point for dependency verification.
    Call this at app startup to check and optionally repair dependencies.

    Returns:
        bool: True if app should continue, False if should exit
    """
    # Check model dependencies first
    if not verify_model_dependencies():
        return False

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
