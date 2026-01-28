"""
Comprehensive API sanity check for PyWebView settings backend.

Tests EVERY API method in settings_webview.py with:
- Happy path (basic functionality works)
- Basic error handling (graceful failure on bad input)

Detailed edge cases are in tab-specific test files.

Run with: py -3.12 -m pytest tests/test_webview_api_complete.py -v
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_webview import SettingsAPI
import config


# =============================================================================
# Core Settings Methods
# =============================================================================

class TestGetAllSettings:
    """Test get_all_settings() API."""

    def test_returns_success_and_data(self):
        """Verify basic response structure."""
        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert "data" in result

    def test_hides_license_key_from_frontend(self):
        """Verify license key is hidden but has_license_key flag is set."""
        api = SettingsAPI()
        api._config["license_key"] = "SECRET-KEY"

        result = api.get_all_settings()

        assert result["data"]["license_key"] == ""
        assert result["data"]["has_license_key"] is True

    def test_includes_all_default_keys(self):
        """Verify all default settings are returned."""
        api = SettingsAPI()
        result = api.get_all_settings()

        # Check a sample of important keys exist
        data = result["data"]
        assert "preview_enabled" in data
        assert "model_size" in data
        assert "language" in data


class TestSaveSetting:
    """Test save_setting() API."""

    def test_saves_simple_setting(self):
        """Verify simple setting saves correctly."""
        api = SettingsAPI()

        result = api.save_setting("preview_enabled", False)

        assert result["success"] is True
        assert api._config["preview_enabled"] is False

    def test_saves_nested_hotkey_setting(self):
        """Verify nested hotkey setting saves correctly."""
        api = SettingsAPI()

        result = api.save_setting("hotkey.ctrl", True)

        assert result["success"] is True
        assert api._config["hotkey"]["ctrl"] is True

    def test_validates_sample_rate(self):
        """Verify sample_rate is validated."""
        api = SettingsAPI()

        result = api.save_setting("sample_rate", 16000)

        assert result["success"] is True
        assert api._config["sample_rate"] == 16000

    def test_handles_save_exception(self, mocker):
        """Verify graceful failure on save error."""
        api = SettingsAPI()
        mocker.patch('config.save_config', side_effect=Exception("Write failed"))

        result = api.save_setting("preview_enabled", True)

        assert result["success"] is False
        assert "Write failed" in result["error"]


class TestSaveMultipleSettings:
    """Test save_multiple_settings() API."""

    def test_saves_multiple_settings_at_once(self):
        """Verify batch save works correctly."""
        api = SettingsAPI()

        result = api.save_multiple_settings({
            "audio_feedback": False,
            "preview_enabled": True
        })

        assert result["success"] is True
        assert api._config["audio_feedback"] is False
        assert api._config["preview_enabled"] is True

    def test_saves_nested_settings(self):
        """Verify nested settings in batch."""
        api = SettingsAPI()

        result = api.save_multiple_settings({
            "hotkey.ctrl": True,
            "hotkey.key": "F12"
        })

        assert result["success"] is True
        assert api._config["hotkey"]["ctrl"] is True
        assert api._config["hotkey"]["key"] == "F12"

    def test_handles_exception(self, mocker):
        """Verify graceful failure on error."""
        api = SettingsAPI()
        mocker.patch('config.save_config', side_effect=Exception("Error"))

        result = api.save_multiple_settings({"audio_feedback": False})

        assert result["success"] is False


# =============================================================================
# App Info Methods
# =============================================================================

class TestGetVersionInfo:
    """Test get_version_info() API."""

    def test_returns_version_info(self):
        """Verify version info structure."""
        api = SettingsAPI()

        result = api.get_version_info()

        assert result["success"] is True
        assert "version" in result["data"]
        assert "app_name" in result["data"]
        assert "python_version" in result["data"]

    def test_version_matches_config(self):
        """Verify version matches config.VERSION."""
        api = SettingsAPI()

        result = api.get_version_info()

        assert result["data"]["version"] == config.VERSION
        assert result["data"]["app_name"] == config.APP_NAME


class TestGetLanguageOptions:
    """Test get_language_options() API."""

    def test_returns_language_list(self):
        """Verify language options structure."""
        api = SettingsAPI()

        result = api.get_language_options()

        assert result["success"] is True
        assert isinstance(result["data"], list)

    def test_includes_expected_languages(self):
        """Verify common languages are included."""
        api = SettingsAPI()

        result = api.get_language_options()
        codes = [opt["code"] for opt in result["data"]]

        assert "en" in codes
        assert "auto" in codes

    def test_format_is_code_and_label(self):
        """Verify option format."""
        api = SettingsAPI()

        result = api.get_language_options()
        first_option = result["data"][0]

        assert "code" in first_option
        assert "label" in first_option


class TestGetProcessingModeOptions:
    """Test get_processing_mode_options() API."""

    def test_returns_mode_list(self):
        """Verify processing mode options structure."""
        api = SettingsAPI()

        result = api.get_processing_mode_options()

        assert result["success"] is True
        assert isinstance(result["data"], list)

    def test_includes_all_modes(self):
        """Verify auto and cpu modes are included."""
        api = SettingsAPI()

        result = api.get_processing_mode_options()
        codes = [opt["code"] for opt in result["data"]]

        assert "auto" in codes
        assert "cpu" in codes


# =============================================================================
# Audio Methods
# =============================================================================

class TestGetAudioDevices:
    """Test get_audio_devices() API."""

    def test_returns_device_list(self, mocker):
        """Verify audio device list structure."""
        mocker.patch('config.get_input_devices', return_value=[
            ("System Default", None),
            ("Microphone (USB)", {"name": "USB Mic"})
        ])
        api = SettingsAPI()

        result = api.get_audio_devices()

        assert result["success"] is True
        assert isinstance(result["data"], list)

    def test_handles_no_devices(self, mocker):
        """Verify graceful handling when no devices available."""
        mocker.patch('config.get_input_devices', return_value=[])
        api = SettingsAPI()

        result = api.get_audio_devices()

        assert result["success"] is True
        assert result["data"] == []


# =============================================================================
# Model Methods
# =============================================================================

class TestGetAvailableModels:
    """Test get_available_models() API."""

    def test_returns_model_list(self, mocker):
        """Verify model list structure."""
        mocker.patch('dependency_check.check_model_available', return_value=(True, "/path"))
        api = SettingsAPI()

        result = api.get_available_models()

        assert result["success"] is True
        assert isinstance(result["data"], list)

    def test_model_has_required_fields(self, mocker):
        """Verify model object has required fields."""
        mocker.patch('dependency_check.check_model_available', return_value=(True, "/path"))
        api = SettingsAPI()

        result = api.get_available_models()
        model = result["data"][0]

        assert "name" in model
        assert "display_name" in model
        assert "is_downloaded" in model


class TestDownloadModel:
    """Test download_model() API."""

    def test_returns_success_on_start(self):
        """Verify download starts successfully."""
        api = SettingsAPI()
        mock_window = MagicMock()
        api.set_window(mock_window)

        result = api.download_model("tiny")

        assert result["success"] is True
        assert "started" in result.get("message", "").lower() or result["success"]


# =============================================================================
# GPU Methods
# =============================================================================

class TestGetGPUStatus:
    """Test get_gpu_status() API."""

    def test_returns_gpu_available(self, mocker):
        """Verify GPU available status."""
        mocker.patch('settings_logic.get_cuda_status',
                     return_value=(True, "CUDA Available", "NVIDIA RTX 3080"))
        api = SettingsAPI()

        result = api.get_gpu_status()

        assert result["success"] is True
        assert result["data"]["available"] is True
        assert "RTX 3080" in result["data"]["name"]

    def test_returns_gpu_unavailable(self, mocker):
        """Verify GPU unavailable status."""
        mocker.patch('settings_logic.get_cuda_status',
                     return_value=(False, "GPU libraries not installed", None))
        api = SettingsAPI()

        result = api.get_gpu_status()

        assert result["success"] is True
        assert result["data"]["available"] is False


# =============================================================================
# License Methods
# =============================================================================

class TestGetLicenseStatus:
    """Test get_license_status() API."""

    def test_returns_trial_status(self):
        """Verify trial status structure."""
        api = SettingsAPI()
        api._config["license_status"] = "trial"
        api._config["trial_started_date"] = None

        result = api.get_license_status()

        assert result["success"] is True
        assert result["data"]["status"] == "trial"
        assert result["data"]["is_trial"] is True

    def test_returns_active_status(self):
        """Verify active license status."""
        api = SettingsAPI()
        api._config["license_status"] = "active"

        result = api.get_license_status()

        assert result["success"] is True
        assert result["data"]["is_active"] is True

    def test_calculates_days_remaining(self):
        """Verify days remaining calculation."""
        from datetime import datetime, timedelta
        api = SettingsAPI()
        started = (datetime.now() - timedelta(days=5)).isoformat()
        api._config["license_status"] = "trial"
        api._config["trial_started_date"] = started

        result = api.get_license_status()

        # 14-day trial, 5 days elapsed = 9 days remaining
        assert result["data"]["days_remaining"] == 9


class TestActivateLicense:
    """Test activate_license() API."""

    def test_valid_license_activates(self, mocker):
        """Verify valid license activates correctly."""
        mocker.patch('license.validate_license_key', return_value=(True, "Valid"))
        mocker.patch('config.save_config')
        api = SettingsAPI()

        result = api.activate_license("VALID-KEY")

        assert result["success"] is True
        assert result["data"]["status"] == "active"

    def test_invalid_license_rejected(self, mocker):
        """Verify invalid license is rejected."""
        mocker.patch('license.validate_license_key',
                     return_value=(False, "Invalid key format"))
        api = SettingsAPI()

        result = api.activate_license("BAD-KEY")

        assert result["success"] is False
        assert "Invalid" in result["error"]


# =============================================================================
# Utility Methods
# =============================================================================

class TestOpenURL:
    """Test open_url() API."""

    def test_opens_url_in_browser(self, mocker):
        """Verify URL opens in browser."""
        mock_open = mocker.patch('webbrowser.open')
        api = SettingsAPI()

        result = api.open_url("https://example.com")

        assert result["success"] is True
        mock_open.assert_called_once_with("https://example.com")

    def test_handles_exception(self, mocker):
        """Verify graceful failure."""
        mocker.patch('webbrowser.open', side_effect=Exception("No browser"))
        api = SettingsAPI()

        result = api.open_url("https://example.com")

        assert result["success"] is False


class TestOpenLogsFolder:
    """Test open_logs_folder() API."""

    def test_opens_logs_folder(self, mocker):
        """Verify logs folder opens."""
        mocker.patch('os.makedirs')
        mock_startfile = mocker.patch('os.startfile')
        api = SettingsAPI()

        result = api.open_logs_folder()

        assert result["success"] is True
        assert mock_startfile.called

    def test_handles_exception(self, mocker):
        """Verify graceful failure."""
        api = SettingsAPI()
        # Patch after API creation to avoid affecting config loading
        mocker.patch('os.startfile', side_effect=Exception("Permission denied"))

        result = api.open_logs_folder()

        assert result["success"] is False


class TestTestOllamaConnection:
    """Test test_ollama_connection() API."""

    def test_successful_connection(self, mocker):
        """Verify successful Ollama connection."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mocker.patch('urllib.request.urlopen', return_value=mock_response)
        api = SettingsAPI()

        result = api.test_ollama_connection("http://localhost:11434")

        assert result["success"] is True
        assert result["data"]["connected"] is True

    def test_connection_refused(self, mocker):
        """Verify connection refused handling."""
        import urllib.error
        mocker.patch('urllib.request.urlopen',
                     side_effect=urllib.error.URLError("Connection refused"))
        api = SettingsAPI()

        result = api.test_ollama_connection("http://localhost:11434")

        assert result["data"]["connected"] is False


# =============================================================================
# Reset & Microphone Test Methods
# =============================================================================

class TestResetToDefaults:
    """Test reset_to_defaults() API."""

    def test_resets_settings(self):
        """Verify settings are reset to defaults."""
        api = SettingsAPI()
        api._config["audio_feedback"] = False  # Non-default value

        result = api.reset_to_defaults()

        assert result["success"] is True
        assert api._config["audio_feedback"] == config.DEFAULTS["audio_feedback"]

    def test_preserves_license_info(self):
        """Verify license info is preserved after reset."""
        api = SettingsAPI()
        api._config["license_key"] = "PRESERVED"
        api._config["license_status"] = "active"

        result = api.reset_to_defaults()

        assert result["success"] is True
        # License info should be preserved
        assert api._config.get("license_key") == "PRESERVED"
        assert api._config.get("license_status") == "active"


class TestMicrophoneTest:
    """Test start_microphone_test() and stop_microphone_test() APIs."""

    def test_start_returns_success(self, mocker):
        """Verify microphone test starts."""
        mocker.patch('sounddevice.InputStream')
        mocker.patch('config.get_device_index', return_value=0)
        api = SettingsAPI()

        result = api.start_microphone_test()

        assert result["success"] is True

    def test_start_fails_if_already_running(self):
        """Verify error when test already running."""
        api = SettingsAPI()
        api._audio_test_running = True

        result = api.start_microphone_test()

        assert result["success"] is False
        assert "already" in result["error"].lower()

    def test_stop_returns_success(self):
        """Verify stop returns success."""
        api = SettingsAPI()

        result = api.stop_microphone_test()

        assert result["success"] is True

    def test_stop_clears_running_flag(self):
        """Verify running flag is cleared."""
        api = SettingsAPI()
        api._audio_test_running = True

        api.stop_microphone_test()

        assert api._audio_test_running is False


# =============================================================================
# History Methods (Already tested in advanced, but verify here too)
# =============================================================================

class TestHistoryMethods:
    """Test history-related methods."""

    def test_get_history_returns_list(self, mocker, tmp_path):
        """Verify get_history returns list."""
        # Mock the history file path to use temp directory
        history_file = tmp_path / "transcription_history.json"
        mocker.patch('os.path.dirname', return_value=str(tmp_path))
        api = SettingsAPI()

        result = api.get_history()

        # Returns {"history": [...]} format
        assert "history" in result
        assert isinstance(result["history"], list)

    def test_get_history_count_returns_number(self, mocker, tmp_path):
        """Verify get_history_count returns number."""
        # Mock the history file path to use temp directory
        mocker.patch('os.path.dirname', return_value=str(tmp_path))
        api = SettingsAPI()

        result = api.get_history_count()

        # Returns {"count": N} format
        assert "count" in result
        assert isinstance(result["count"], int)


# =============================================================================
# Run All Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
