"""
MurmurTone Settings GUI - PyWebView Version
A modern HTML/CSS/JS-based settings interface using PyWebView.
"""
import webview
import threading
import os
import sys
import json
import math

import sounddevice as sd
import numpy as np

import config
import settings_logic

# Get the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(BASE_DIR, "ui")


class SettingsAPI:
    """
    API class exposed to JavaScript via pywebview.api.
    All methods return JSON-serializable dicts.
    """

    def __init__(self):
        self._config = config.load_config()
        self._window = None
        # Audio test state
        self._audio_test_running = False
        self._audio_test_stream = None

    def set_window(self, window):
        """Store reference to window for evaluate_js calls."""
        self._window = window

    # =========================================================================
    # Core Settings Methods
    # =========================================================================

    def get_all_settings(self):
        """
        Return all current settings.
        Called on page load to populate UI.
        """
        try:
            # Reload config to get fresh values
            self._config = config.load_config()

            # Don't expose encrypted license key to frontend
            safe_config = self._config.copy()
            if "license_key" in safe_config:
                # Only indicate if key exists, don't expose it
                safe_config["has_license_key"] = bool(safe_config.get("license_key"))
                safe_config["license_key"] = ""  # Don't send to frontend

            return {"success": True, "data": safe_config}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Validators for settings that need input validation
    _VALIDATORS = {
        "sample_rate": settings_logic.validate_sample_rate,
        "silence_duration_sec": settings_logic.validate_silence_duration,
        "noise_gate_threshold_db": settings_logic.validate_noise_threshold,
        # audio_feedback_volume removed - conversion happens in JS, validation below
        "preview_auto_hide_delay": settings_logic.validate_preview_delay,
        # Text tab validators
        "custom_fillers": "_validate_custom_fillers",
        "custom_dictionary": "_validate_custom_dictionary",
        "custom_commands": "_validate_custom_commands",
        "custom_vocabulary": "_validate_custom_vocabulary",
    }

    @staticmethod
    def _validate_custom_fillers(value):
        """Validate and normalize custom filler words array."""
        if not isinstance(value, list):
            raise ValueError("custom_fillers must be an array")

        # Normalize: lowercase, trim, remove empties, deduplicate
        normalized = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue  # Skip non-strings silently
            word = item.strip().lower()
            if word and word not in seen:
                normalized.append(word)
                seen.add(word)

        return normalized

    @staticmethod
    def _validate_custom_dictionary(value):
        """Validate custom dictionary entries."""
        if not isinstance(value, list):
            raise ValueError("custom_dictionary must be an array")

        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise ValueError(f"Dictionary entry {i} must be an object")
            if "from" not in item or "to" not in item:
                raise ValueError(f"Dictionary entry {i} missing 'from' or 'to' keys")
            if not str(item.get("from", "")).strip():
                raise ValueError(f"Dictionary entry {i} has empty 'from' value")

        return value

    @staticmethod
    def _validate_custom_commands(value):
        """Validate text shortcuts entries."""
        if not isinstance(value, list):
            raise ValueError("custom_commands must be an array")

        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise ValueError(f"Shortcut entry {i} must be an object")
            if "trigger" not in item or "replacement" not in item:
                raise ValueError(f"Shortcut entry {i} missing 'trigger' or 'replacement' keys")
            if not str(item.get("trigger", "")).strip():
                raise ValueError(f"Shortcut entry {i} has empty trigger")

        return value

    @staticmethod
    def _validate_custom_vocabulary(value):
        """Validate custom vocabulary words."""
        if not isinstance(value, list):
            raise ValueError("custom_vocabulary must be an array")

        # Ensure all items are non-empty strings
        normalized = []
        for item in value:
            if isinstance(item, str) and item.strip():
                normalized.append(item.strip())

        return normalized

    def save_setting(self, key, value):
        """
        Save a single setting.
        Supports nested keys like "hotkey.ctrl" using dot notation.
        """
        try:
            # Apply validation if validator exists for this key
            if key in self._VALIDATORS:
                validator = self._VALIDATORS[key]
                # If validator is a string (method name), call it as a method
                if isinstance(validator, str):
                    value = getattr(self, validator)(value)
                else:
                    value = validator(value)

            # Custom validation for volume (0-100 percentage)
            if key == "audio_feedback_volume":
                value = max(0, min(100, int(value)))

            # Validate URL fields
            if key == "ollama_url":
                value = settings_logic.validate_url(value, "http://localhost:11434")

            # Special handling for specific keys
            if key == "start_with_windows":
                # Update Windows registry for startup
                config.set_startup_enabled(value)

            if key == "input_device":
                # Normalize device format: None for system default, dict for specific device
                if value:
                    value = {"name": value}  # Convert string ID to expected dict format
                else:
                    value = None  # Empty string means system default

            # Handle nested keys (e.g., "hotkey.ctrl")
            if "." in key:
                parts = key.split(".")
                target = self._config
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = value
            else:
                self._config[key] = value

            # Persist to disk
            config.save_config(self._config)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_multiple_settings(self, settings_dict):
        """
        Save multiple settings at once.
        More efficient than calling save_setting multiple times.
        """
        try:
            for key, value in settings_dict.items():
                if "." in key:
                    parts = key.split(".")
                    target = self._config
                    for part in parts[:-1]:
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    target[parts[-1]] = value
                else:
                    self._config[key] = value

            config.save_config(self._config)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # App Info
    # =========================================================================

    def get_version_info(self):
        """Return app version and related info."""
        try:
            return {
                "success": True,
                "data": {
                    "version": config.VERSION,
                    "app_name": config.APP_NAME,
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_language_options(self):
        """Return available language options from config."""
        try:
            # LANGUAGE_LABELS is a dict: {"auto": "Auto-detect", "en": "English", ...}
            options = []
            for code, label in config.LANGUAGE_LABELS.items():
                options.append({"code": code, "label": label})
            return {"success": True, "data": options}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_processing_mode_options(self):
        """Return available processing mode options from config."""
        try:
            # PROCESSING_MODE_LABELS is a dict: {"auto": "Auto", "cpu": "CPU Only", ...}
            options = []
            for code, label in config.PROCESSING_MODE_LABELS.items():
                options.append({"code": code, "label": label})
            return {"success": True, "data": options}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Audio Devices
    # =========================================================================

    def get_audio_devices(self):
        """Return list of available audio input devices."""
        try:
            devices = config.get_input_devices()
            device_list = []
            for display_name, device_info in devices:
                device_list.append({
                    "name": display_name,
                    "id": device_info["name"] if device_info else None,
                    "is_default": device_info is None  # First item is always default
                })
            return {"success": True, "data": device_list}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def refresh_audio_devices(self):
        """Refresh and return the audio device list."""
        return self.get_audio_devices()

    # =========================================================================
    # Model Info
    # =========================================================================

    def get_available_models(self):
        """Return list of available Whisper models with download status."""
        try:
            from dependency_check import check_model_available

            models = []
            for model_name in config.MODEL_OPTIONS:
                display_name = config.MODEL_DISPLAY_NAMES.get(model_name, model_name)
                size_mb = config.MODEL_SIZES_MB.get(model_name, 0)

                is_bundled = model_name in config.BUNDLED_MODELS
                # Check actual download status (bundled dir or HuggingFace cache)
                is_downloaded, model_path = check_model_available(model_name)

                models.append({
                    "name": model_name,
                    "display_name": display_name,
                    "size_mb": size_mb,
                    "is_bundled": is_bundled,
                    "is_downloaded": is_downloaded
                })

            return {"success": True, "data": models}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_model(self, model_name):
        """
        Start downloading a Whisper model.
        Progress is reported back to JavaScript via evaluate_js.
        """
        def do_download():
            try:
                import requests
                import zipfile
                import tempfile
                from dependency_check import get_models_dir, check_model_available

                # Get download URL
                download_url = config.MODEL_DOWNLOAD_URLS.get(model_name)
                if not download_url:
                    self._window.evaluate_js(
                        f'window.onModelDownloadError("No download URL for model: {model_name}")'
                    )
                    return

                # Report starting
                self._window.evaluate_js('window.onModelDownloadProgress(0, "Connecting...")')

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
                            percent = int((downloaded / total_size) * 80)  # 80% for download
                            size_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            self._window.evaluate_js(
                                f'window.onModelDownloadProgress({percent}, "Downloading: {size_mb:.1f} / {total_mb:.1f} MB")'
                            )

                temp_zip.close()

                # Extract
                self._window.evaluate_js('window.onModelDownloadProgress(85, "Extracting model...")')
                models_dir = get_models_dir()
                os.makedirs(models_dir, exist_ok=True)

                with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
                    zip_ref.extractall(models_dir)

                # Verify
                self._window.evaluate_js('window.onModelDownloadProgress(95, "Verifying...")')
                is_available, _ = check_model_available(model_name)
                if not is_available:
                    raise Exception("Model extraction failed - files not found")

                # Cleanup temp file
                try:
                    os.unlink(temp_zip.name)
                except Exception:
                    pass

                # Success
                self._window.evaluate_js('window.onModelDownloadProgress(100, "Complete!")')
                self._window.evaluate_js('window.onModelDownloadComplete(true)')

            except Exception as e:
                error_msg = str(e).replace("'", "\\'").replace('"', '\\"')
                self._window.evaluate_js(f'window.onModelDownloadError("{error_msg}")')

        # Start download in background thread
        thread = threading.Thread(target=do_download, daemon=True)
        thread.start()
        return {"success": True, "message": "Download started"}

    def get_history(self):
        """Get transcription history."""
        history_file = os.path.join(os.path.dirname(__file__), "transcription_history.json")
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return {"history": history}
        except Exception as e:
            print(f"Failed to load history: {e}")
        return {"history": []}

    def get_history_count(self):
        """Get the count of history items."""
        result = self.get_history()
        return {"count": len(result.get("history", []))}

    def clear_history(self):
        """Clear all transcription history."""
        history_file = os.path.join(os.path.dirname(__file__), "transcription_history.json")
        try:
            if os.path.exists(history_file):
                os.remove(history_file)
            return {"success": True}
        except Exception as e:
            print(f"Failed to clear history: {e}")
            return {"success": False, "error": str(e)}

    def export_history(self, format_type='json'):
        """Export history to a file chosen by user.

        Args:
            format_type: Export format - 'txt', 'csv', or 'json'
        """
        try:
            ext_map = {'txt': '.txt', 'csv': '.csv', 'json': '.json'}
            type_map = {
                'txt': ('Text Files (*.txt)', 'All Files (*.*)'),
                'csv': ('CSV Files (*.csv)', 'All Files (*.*)'),
                'json': ('JSON Files (*.json)', 'All Files (*.*)')
            }

            extension = ext_map.get(format_type, '.json')
            file_types = type_map.get(format_type, type_map['json'])

            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=f'transcription_history{extension}',
                file_types=file_types
            )
            if result:
                filename = result if isinstance(result, str) else result[0]
                history = self.get_history().get("history", [])

                with open(filename, 'w', encoding='utf-8') as f:
                    if format_type == 'txt':
                        f.write("Transcription History\n")
                        f.write("=" * 60 + "\n\n")
                        for item in history:
                            f.write(f"[{item.get('timestamp', 'Unknown')}]\n")
                            f.write(f"{item.get('text', '')}\n\n")
                    elif format_type == 'csv':
                        import csv
                        writer = csv.writer(f)
                        writer.writerow(["Timestamp", "Text", "Characters"])
                        for item in history:
                            writer.writerow([
                                item.get('timestamp', ''),
                                item.get('text', ''),
                                len(item.get('text', ''))
                            ])
                    else:  # json
                        json.dump(history, f, indent=2, ensure_ascii=False)

                return {"success": True, "filename": os.path.basename(filename)}
            return {"success": False, "cancelled": True}
        except Exception as e:
            print(f"Failed to export history: {e}")
            return {"success": False, "error": str(e)}

    def get_gpu_status(self):
        """Check if GPU/CUDA is available for processing."""
        try:
            # Use settings_logic for consistent detection with Tkinter version
            is_available, status_msg, gpu_name = settings_logic.get_cuda_status()
            return {
                "success": True,
                "data": {
                    "available": is_available,
                    "name": gpu_name,
                    "status": status_msg
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def install_gpu_support(self):
        """
        Attempt to install CUDA libraries for GPU acceleration.
        For bundled exe users, this downloads pre-packaged DLLs.
        """
        try:
            import subprocess
            import sys

            # Try pip install for development environments
            packages = [
                "nvidia-cublas-cu12",
                "nvidia-cudnn-cu12"
            ]

            for package in packages:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": f"Failed to install {package}. Please install CUDA manually."
                    }

            return {
                "success": True,
                "message": "GPU support installed. Please restart the application."
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Installation timed out. Please try again or install manually."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Installation failed: {str(e)}"
            }

    # =========================================================================
    # Microphone Test
    # =========================================================================

    def start_microphone_test(self):
        """Start audio level monitoring for noise gate calibration."""
        if self._audio_test_running:
            return {"success": False, "error": "Already running"}

        try:
            self._audio_test_running = True
            device_idx = config.get_device_index(self._config.get("input_device"))
            sample_rate = self._config.get("sample_rate", 16000)

            def audio_callback(indata, frames, time_info, status):
                if not self._audio_test_running:
                    raise sd.CallbackAbort()
                # Calculate RMS level in dB
                rms = np.sqrt(np.mean(indata**2))
                if rms > 0:
                    db = 20 * math.log10(rms)
                else:
                    db = -60
                # Clamp to meter range
                db = max(-60, min(-20, db))
                # Send to frontend
                if self._window:
                    self._window.evaluate_js(f'window.onAudioLevel && window.onAudioLevel({db:.1f})')

            self._audio_test_stream = sd.InputStream(
                device=device_idx,
                channels=1,
                samplerate=sample_rate,
                callback=audio_callback,
                blocksize=1024
            )
            self._audio_test_stream.start()
            return {"success": True}
        except Exception as e:
            self._audio_test_running = False
            return {"success": False, "error": str(e)}

    def stop_microphone_test(self):
        """Stop audio level monitoring."""
        self._audio_test_running = False
        if self._audio_test_stream:
            try:
                self._audio_test_stream.stop()
                self._audio_test_stream.close()
            except Exception:
                pass
            self._audio_test_stream = None
        return {"success": True}

    # =========================================================================
    # License (Status Only - Key Stays in Python)
    # =========================================================================

    def get_license_status(self):
        """Return license status without exposing the key."""
        try:
            status = self._config.get("license_status", "trial")
            trial_started = self._config.get("trial_started_date")

            # Calculate days remaining for trial
            days_remaining = None
            if status == "trial" and trial_started:
                from datetime import datetime
                try:
                    start = datetime.fromisoformat(trial_started)
                    elapsed = (datetime.now() - start).days
                    days_remaining = max(0, 14 - elapsed)  # 14-day trial
                except:
                    days_remaining = 14

            return {
                "success": True,
                "data": {
                    "status": status,
                    "is_trial": status == "trial",
                    "is_active": status == "active",
                    "days_remaining": days_remaining,
                    "has_key": bool(self._config.get("license_key"))
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def activate_license(self, key):
        """
        Validate and activate a license key.
        Key validation happens in Python, only status is returned.
        """
        try:
            # Import license module for validation
            import license as license_module

            # Validate the key (returns tuple: is_valid, message)
            is_valid, message = license_module.validate_license_key(key, self._config)

            if is_valid:
                self._config["license_key"] = key
                self._config["license_status"] = "active"
                config.save_config(self._config)
                return {"success": True, "data": {"status": "active"}}
            else:
                return {"success": False, "error": message or "Invalid license key"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def test_ollama_connection(self, url):
        """Test connection to Ollama server."""
        try:
            import urllib.request
            import urllib.error

            # Clean up URL
            url = url.rstrip('/')
            test_url = f"{url}/api/tags"

            req = urllib.request.Request(test_url, method='GET')
            req.add_header('Accept', 'application/json')

            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "data": {"connected": True}
                    }
                else:
                    return {
                        "success": True,
                        "data": {"connected": False},
                        "error": f"HTTP {response.status}"
                    }
        except urllib.error.URLError as e:
            return {
                "success": True,
                "data": {"connected": False},
                "error": str(e.reason)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_url(self, url):
        """Open a URL in the default browser."""
        try:
            import webbrowser
            webbrowser.open(url)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_logs_folder(self):
        """Open the logs folder in the system file explorer."""
        try:
            logs_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(logs_dir, exist_ok=True)
            os.startfile(logs_dir)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reset_to_defaults(self):
        """Reset all settings to defaults (except license)."""
        try:
            # Preserve license info (including encrypted key for persistence)
            license_key = self._config.get("license_key", "")
            license_key_encrypted = self._config.get("license_key_encrypted", "")
            license_status = self._config.get("license_status", "trial")
            trial_started = self._config.get("trial_started_date")

            # Reset to defaults
            self._config = config.DEFAULTS.copy()

            # Restore license info
            self._config["license_key"] = license_key
            if license_key_encrypted:
                self._config["license_key_encrypted"] = license_key_encrypted
            self._config["license_status"] = license_status
            self._config["trial_started_date"] = trial_started

            config.save_config(self._config)

            # Reload config to get decrypted license key in memory
            self._config = config.load_config()

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


def create_window():
    """Create and run the PyWebView window."""
    api = SettingsAPI()

    # Create window
    window = webview.create_window(
        title=f"{config.APP_NAME} Settings",
        url=os.path.join(UI_DIR, "index.html"),
        js_api=api,
        width=900,
        height=650,
        min_size=(800, 500),
        resizable=True,
        background_color="#0f172a"  # Match dark theme
    )

    # Store window reference in API for evaluate_js calls
    api.set_window(window)

    return window


def main():
    """Entry point for the settings GUI."""
    window = create_window()

    # Start webview (blocks until window is closed)
    webview.start(debug=True)  # debug=True for development


if __name__ == "__main__":
    main()
