"""
Configuration management for MurmurTone.
Handles loading/saving settings to JSON file.
"""
import json
import os
import sounddevice as sd

# App info
APP_NAME = "MurmurTone"
VERSION = "1.0.0"

# Default settings
DEFAULTS = {
    "model_size": "tiny.en",
    "sample_rate": 16000,
    "language": "en",
    "hotkey": {
        "ctrl": True,
        "shift": True,
        "alt": False,
        "key": "space"
    },
    "recording_mode": "push_to_talk",  # "push_to_talk" or "auto_stop"
    "silence_duration_sec": 2.0,
    "audio_feedback": True,
    "input_device": None  # None = system default, or device name string
}

MODEL_OPTIONS = ["tiny.en", "base.en", "small.en", "medium.en"]
LANGUAGE_OPTIONS = ["en", "auto"]
RECORDING_MODE_OPTIONS = ["push_to_talk", "auto_stop"]


def get_config_path():
    """Get path to settings.json in user's AppData directory."""
    app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
    config_dir = os.path.join(app_data, "MurmurTone")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "settings.json")


def load_config():
    """Load settings from JSON file, return defaults if not found."""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                saved = json.load(f)
                # Merge with defaults to handle missing keys
                config = DEFAULTS.copy()
                config.update(saved)
                # Ensure hotkey has all required keys
                if "hotkey" in saved:
                    hotkey = DEFAULTS["hotkey"].copy()
                    hotkey.update(saved["hotkey"])
                    config["hotkey"] = hotkey
                return config
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULTS.copy()


def save_config(config):
    """Save settings to JSON file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def hotkey_to_string(hotkey):
    """Convert hotkey dict to display string like 'Ctrl+Shift+Space'."""
    parts = []
    if hotkey.get("ctrl"):
        parts.append("Ctrl")
    if hotkey.get("alt"):
        parts.append("Alt")
    if hotkey.get("shift"):
        parts.append("Shift")
    key = hotkey.get("key", "space")
    parts.append(key.capitalize() if len(key) > 1 else key.upper())
    return "+".join(parts)


def get_input_devices():
    """
    Get list of available input devices.
    Returns list of (display_name, device_info) tuples.
    First item is always ("System Default (device name)", None).
    Only shows WASAPI devices (respects Windows enable/disable settings).
    """
    # Get default device name
    default_label = "System Default"
    try:
        default_idx = sd.default.device[0]  # Input device index
        if default_idx is not None and default_idx >= 0:
            default_dev = sd.query_devices(default_idx)
            if default_dev:
                default_name = default_dev['name']
                # Try to find WASAPI version of this device for full name
                all_devices = sd.query_devices()
                hostapis = sd.query_hostapis()
                for i, dev in enumerate(all_devices):
                    if dev["max_input_channels"] > 0:
                        hostapi_name = hostapis[dev["hostapi"]]["name"]
                        # Match by prefix (MME truncates, WASAPI has full name)
                        if "WASAPI" in hostapi_name:
                            if dev["name"].startswith(default_name[:30]) or default_name.startswith(dev["name"][:30]):
                                default_name = dev["name"]
                                break
                # Shorten: just use the part before parentheses for cleaner display
                short_name = default_name.split(" (")[0] if " (" in default_name else default_name
                default_label = f"System Default ({short_name})"
    except Exception:
        pass

    devices = [(default_label, None)]

    try:
        all_devices = sd.query_devices()
        hostapis = sd.query_hostapis()

        for i, dev in enumerate(all_devices):
            if dev["max_input_channels"] > 0:
                hostapi_idx = dev["hostapi"]
                hostapi_name = hostapis[hostapi_idx]["name"] if hostapi_idx < len(hostapis) else ""

                # Only include WASAPI devices (these respect Windows enable/disable)
                if "WASAPI" not in hostapi_name:
                    continue

                name = dev["name"]
                device_info = {
                    "name": name,
                    "index": i,
                    "hostapi": hostapi_idx,
                    "channels": dev["max_input_channels"]
                }
                devices.append((name, device_info))

    except Exception:
        pass  # Return just "System Default" if enumeration fails

    return devices


def get_device_index(saved_device):
    """
    Get the sounddevice index for a saved device config.
    Returns None (system default) if device not found.

    saved_device can be:
    - None: use system default
    - dict with "name" key: find device by name
    - str: legacy format, treat as device name
    """
    if saved_device is None:
        return None

    # Handle legacy string format
    if isinstance(saved_device, str):
        device_name = saved_device
    elif isinstance(saved_device, dict):
        device_name = saved_device.get("name")
    else:
        return None

    if not device_name:
        return None

    try:
        all_devices = sd.query_devices()
        for i, dev in enumerate(all_devices):
            if dev["max_input_channels"] > 0 and dev["name"] == device_name:
                return i
    except Exception:
        pass

    return None  # Device not found, fall back to default


def is_device_available(saved_device):
    """Check if the saved device is currently available."""
    if saved_device is None:
        return True  # System default is always "available"
    return get_device_index(saved_device) is not None
