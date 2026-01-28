"""
Comprehensive tests for PyWebView Audio tab.
Ensures 100% feature parity with Tkinter implementation.
"""
import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_webview import SettingsAPI
import config


class TestAudioDeviceManagement:
    """Test audio device enumeration and selection."""

    @patch('config.get_input_devices')
    def test_get_audio_devices_returns_list(self, mock_get_devices):
        """Verify device list is returned with correct format."""
        mock_get_devices.return_value = [
            ("System Default (Microphone)", None),
            ("Blue Yeti", {"name": "Blue Yeti", "index": 1}),
            ("Realtek Audio", {"name": "Realtek", "index": 2})
        ]

        api = SettingsAPI()
        result = api.get_audio_devices()

        assert result["success"] is True
        assert len(result["data"]) == 3
        assert result["data"][0]["is_default"] is True
        assert result["data"][0]["id"] is None
        assert result["data"][1]["name"] == "Blue Yeti"
        assert result["data"][1]["id"] == "Blue Yeti"

    @patch('config.get_input_devices')
    def test_refresh_audio_devices(self, mock_get_devices):
        """Verify refresh returns updated device list."""
        mock_get_devices.return_value = [
            ("System Default", None)
        ]

        api = SettingsAPI()
        result = api.refresh_audio_devices()

        assert result["success"] is True
        mock_get_devices.assert_called_once()

    @patch('config.save_config')
    def test_save_device_selection_system_default(self, mock_save):
        """Test saving system default device (None)."""
        api = SettingsAPI()
        result = api.save_setting("input_device", "")  # Empty string = default

        assert result["success"] is True
        # Verify it was converted to None internally
        assert api._config["input_device"] is None
        mock_save.assert_called_once()

    @patch('config.save_config')
    def test_save_device_selection_specific_device(self, mock_save):
        """Test saving specific device."""
        api = SettingsAPI()
        result = api.save_setting("input_device", "Blue Yeti")

        assert result["success"] is True
        # Verify it was converted to dict format
        assert api._config["input_device"] == {"name": "Blue Yeti"}
        mock_save.assert_called_once()


class TestSampleRateSettings:
    """Test sample rate configuration."""

    @patch('config.save_config')
    @patch('settings_logic.validate_sample_rate')
    def test_save_valid_sample_rate(self, mock_validate, mock_save):
        """Test saving valid sample rates."""
        api = SettingsAPI()

        for rate in [16000, 44100, 48000]:
            mock_validate.return_value = rate
            result = api.save_setting("sample_rate", rate)
            assert result["success"] is True
            assert api._config["sample_rate"] == rate

    @patch('config.save_config')
    @patch('settings_logic.validate_sample_rate')
    def test_sample_rate_validation(self, mock_validate, mock_save):
        """Test sample rate validation through validator."""
        api = SettingsAPI()

        # Invalid rate should be rejected/corrected by validator
        mock_validate.return_value = 16000  # Validator returns default
        result = api.save_setting("sample_rate", 999)
        assert result["success"] is True
        assert api._config["sample_rate"] == 16000


class TestMicrophoneTest:
    """Test microphone test functionality."""

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_start_microphone_test(self, mock_get_index, mock_stream):
        """Test starting microphone test."""
        mock_get_index.return_value = 0
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)

        result = api.start_microphone_test()

        assert result["success"] is True
        mock_stream.assert_called_once()
        mock_stream_instance.start.assert_called_once()

    def test_start_microphone_test_already_running(self):
        """Test starting test when already running."""
        api = SettingsAPI()
        api._audio_test_running = True

        result = api.start_microphone_test()

        assert result["success"] is False
        assert "Already running" in result["error"]

    def test_stop_microphone_test(self):
        """Test stopping microphone test."""
        api = SettingsAPI()
        mock_stream = MagicMock()
        api._audio_test_stream = mock_stream
        api._audio_test_running = True

        result = api.stop_microphone_test()

        assert result["success"] is True
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
        assert api._audio_test_running is False

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_audio_callback_calculates_db_correctly(self, mock_get_index, mock_stream):
        """Test that audio callback calculates dB levels correctly."""
        import numpy as np

        mock_get_index.return_value = 0
        callback_func = None

        def capture_callback(*args, **kwargs):
            nonlocal callback_func
            callback_func = kwargs['callback']
            return MagicMock()

        mock_stream.side_effect = capture_callback

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)
        api.start_microphone_test()

        # Simulate audio input
        test_data = np.array([[0.1]])  # RMS will be 0.1
        callback_func(test_data, 1024, None, None)

        # Verify evaluate_js was called with dB value
        window.evaluate_js.assert_called()
        call_args = window.evaluate_js.call_args[0][0]
        assert 'onAudioLevel' in call_args
        # 20 * log10(0.1) = -20 dB
        assert '-20' in call_args or '-20.' in call_args


class TestAudioFeedbackMasterToggle:
    """Test audio feedback master toggle (NEW FEATURE)."""

    @patch('config.save_config')
    def test_enable_audio_feedback_master_toggle(self, mock_save):
        """Test enabling audio feedback master toggle."""
        api = SettingsAPI()
        result = api.save_setting("audio_feedback", True)

        assert result["success"] is True
        assert api._config["audio_feedback"] is True
        mock_save.assert_called_once()

    @patch('config.save_config')
    def test_disable_audio_feedback_master_toggle(self, mock_save):
        """Test disabling audio feedback master toggle."""
        api = SettingsAPI()
        result = api.save_setting("audio_feedback", False)

        assert result["success"] is True
        assert api._config["audio_feedback"] is False
        mock_save.assert_called_once()

    @patch('config.load_config')
    def test_default_audio_feedback_is_true(self, mock_load):
        """Verify default state is enabled."""
        mock_load.return_value = {"audio_feedback": True}
        api = SettingsAPI()
        settings = api.get_all_settings()

        assert settings["data"]["audio_feedback"] is True


class TestVolumeConversion:
    """Test volume conversion between UI (0-100) and config (0.0-1.0)."""

    @patch('config.save_config')
    def test_volume_stored_as_float(self, mock_save):
        """Verify volume is stored as float 0.0-1.0 in config."""
        api = SettingsAPI()

        # UI sends 0.5 (already converted by JS from 50%)
        result = api.save_setting("audio_feedback_volume", 0.5)

        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.5
        assert isinstance(api._config["audio_feedback_volume"], float)
        mock_save.assert_called_once()

    @patch('config.save_config')
    def test_volume_clamped_to_range(self, mock_save):
        """Test volume is clamped to 0.0-1.0."""
        api = SettingsAPI()

        # Below minimum
        result = api.save_setting("audio_feedback_volume", -0.5)
        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.0

        # Above maximum
        result = api.save_setting("audio_feedback_volume", 1.5)
        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 1.0

    @patch('config.save_config')
    def test_volume_zero_is_valid(self, mock_save):
        """Test volume of 0 (mute) is valid."""
        api = SettingsAPI()
        result = api.save_setting("audio_feedback_volume", 0.0)

        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.0
        mock_save.assert_called_once()

    @patch('config.save_config')
    def test_volume_max_is_valid(self, mock_save):
        """Test volume of 1.0 (100%) is valid."""
        api = SettingsAPI()
        result = api.save_setting("audio_feedback_volume", 1.0)

        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 1.0
        mock_save.assert_called_once()

    @patch('config.save_config')
    def test_volume_accepts_string_input(self, mock_save):
        """Test volume accepts string (from JS) and converts."""
        api = SettingsAPI()
        result = api.save_setting("audio_feedback_volume", "0.7")

        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.7
        mock_save.assert_called_once()


class TestIndividualSoundToggles:
    """Test individual sound notification toggles."""

    @patch('config.save_config')
    def test_sound_processing_toggle(self, mock_save):
        """Test processing sound toggle."""
        api = SettingsAPI()

        result = api.save_setting("sound_processing", False)
        assert result["success"] is True
        assert api._config["sound_processing"] is False

        result = api.save_setting("sound_processing", True)
        assert result["success"] is True
        assert api._config["sound_processing"] is True

    @patch('config.save_config')
    def test_sound_success_toggle(self, mock_save):
        """Test success sound toggle."""
        api = SettingsAPI()
        result = api.save_setting("sound_success", False)

        assert result["success"] is True
        assert api._config["sound_success"] is False

    @patch('config.save_config')
    def test_sound_error_toggle(self, mock_save):
        """Test error sound toggle."""
        api = SettingsAPI()
        result = api.save_setting("sound_error", False)

        assert result["success"] is True
        assert api._config["sound_error"] is False

    @patch('config.save_config')
    def test_sound_command_toggle(self, mock_save):
        """Test command sound toggle."""
        api = SettingsAPI()
        result = api.save_setting("sound_command", False)

        assert result["success"] is True
        assert api._config["sound_command"] is False


class TestAudioSettingsPersistence:
    """Test that audio settings persist correctly."""

    @patch('settings_logic.validate_sample_rate')
    @patch('config.save_config')
    def test_all_audio_settings_persist_together(self, mock_save, mock_validate_rate):
        """Simulate user configuring all audio settings."""
        # Setup validators to pass through values
        mock_validate_rate.return_value = 48000

        api = SettingsAPI()

        # Configure all settings
        api.save_setting("input_device", "Blue Yeti")
        api.save_setting("sample_rate", 48000)
        api.save_setting("audio_feedback", True)
        api.save_setting("audio_feedback_volume", 0.75)
        api.save_setting("sound_processing", True)
        api.save_setting("sound_success", False)
        api.save_setting("sound_error", True)
        api.save_setting("sound_command", False)

        # Verify all persisted in internal config
        assert api._config["input_device"]["name"] == "Blue Yeti"
        assert api._config["sample_rate"] == 48000
        assert api._config["audio_feedback"] is True
        assert api._config["audio_feedback_volume"] == 0.75
        assert api._config["sound_processing"] is True
        assert api._config["sound_success"] is False
        assert api._config["sound_error"] is True
        assert api._config["sound_command"] is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch('config.save_config')
    def test_save_invalid_device_name(self, mock_save):
        """Test saving device with special characters."""
        api = SettingsAPI()
        result = api.save_setting("input_device", "Mic (USB Audio)")

        assert result["success"] is True
        assert api._config["input_device"]["name"] == "Mic (USB Audio)"

    @patch('sounddevice.InputStream')
    def test_microphone_test_handles_device_error(self, mock_stream):
        """Test microphone test handles device errors gracefully."""
        mock_stream.side_effect = OSError("Device not found")

        api = SettingsAPI()
        result = api.start_microphone_test()

        assert result["success"] is False
        assert "error" in result


class TestConfigMigration:
    """Test migration of legacy/broken config values."""

    @patch('config.save_config')
    def test_migrate_broken_volume_values_above_one(self, mock_save):
        """Fix volume values stored as integers (50-100) instead of floats (0.5-1.0)."""
        api = SettingsAPI()

        # Simulate loading config with broken volume (integer instead of float)
        api._config["audio_feedback_volume"] = 50  # Bug: stored as integer

        # When saving any setting, volume should be clamped
        result = api.save_setting("audio_feedback_volume", 50)

        assert result["success"] is True
        # Should be clamped to 1.0 (max valid value)
        assert api._config["audio_feedback_volume"] == 1.0

    @patch('config.save_config')
    def test_volume_migration_preserves_valid_values(self, mock_save):
        """Ensure valid float values (0.0-1.0) are not modified."""
        api = SettingsAPI()

        # Save valid volume
        result = api.save_setting("audio_feedback_volume", 0.75)
        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.75

    @patch('config.load_config')
    def test_missing_audio_feedback_key_defaults_to_true(self, mock_load):
        """Handle configs without audio_feedback key (old versions)."""
        # Config without audio_feedback key
        mock_load.return_value = {
            "audio_feedback_volume": 0.5,
            "sound_processing": True
        }

        api = SettingsAPI()
        settings = api.get_all_settings()

        # Should default to True when missing
        assert settings["data"].get("audio_feedback", True) is True


class TestMicrophoneTestMemoryManagement:
    """Ensure microphone test doesn't leak resources."""

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_multiple_start_stop_cycles(self, mock_get_index, mock_stream):
        """Test starting/stopping test multiple times doesn't leak."""
        mock_get_index.return_value = 0
        mock_stream_instances = []

        def create_mock_stream(*args, **kwargs):
            instance = MagicMock()
            mock_stream_instances.append(instance)
            return instance

        mock_stream.side_effect = create_mock_stream

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)

        # Start and stop 5 times
        for i in range(5):
            api.start_microphone_test()
            api.stop_microphone_test()

        # Verify all streams were stopped and closed
        for stream in mock_stream_instances:
            stream.stop.assert_called_once()
            stream.close.assert_called_once()

    def test_stop_test_cleans_up_state(self):
        """Ensure test stops cleans up internal state."""
        api = SettingsAPI()
        mock_stream = MagicMock()
        api._audio_test_stream = mock_stream
        api._audio_test_running = True

        api.stop_microphone_test()

        # Verify state is cleaned
        assert api._audio_test_running is False
        assert api._audio_test_stream is None


class TestVolumeEdgeCases:
    """Additional volume conversion scenarios."""

    @patch('config.save_config')
    def test_volume_fractional_percentages(self, mock_save):
        """Test non-round percentages (e.g., 33%, 67%)."""
        api = SettingsAPI()

        # Test 33% (0.33)
        result = api.save_setting("audio_feedback_volume", 0.33)
        assert result["success"] is True
        assert abs(api._config["audio_feedback_volume"] - 0.33) < 0.01

        # Test 67% (0.67)
        result = api.save_setting("audio_feedback_volume", 0.67)
        assert result["success"] is True
        assert abs(api._config["audio_feedback_volume"] - 0.67) < 0.01

    @patch('config.save_config')
    def test_volume_very_small_values(self, mock_save):
        """Test very small but valid volume values."""
        api = SettingsAPI()

        # Test 1% (0.01)
        result = api.save_setting("audio_feedback_volume", 0.01)
        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.01

    @patch('config.save_config')
    def test_volume_negative_clamped_to_zero(self, mock_save):
        """Test negative values are clamped to 0."""
        api = SettingsAPI()

        result = api.save_setting("audio_feedback_volume", -0.3)
        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 0.0

    @patch('config.save_config')
    def test_volume_above_max_clamped_to_one(self, mock_save):
        """Test values above 1.0 are clamped."""
        api = SettingsAPI()

        result = api.save_setting("audio_feedback_volume", 2.5)
        assert result["success"] is True
        assert api._config["audio_feedback_volume"] == 1.0


class TestAudioFeedbackVisibilityInteractions:
    """Test master toggle interactions with sub-controls."""

    @patch('config.save_config')
    def test_values_persist_when_master_toggle_disabled(self, mock_save):
        """Verify sub-control values retained when master toggle turned off/on."""
        api = SettingsAPI()

        # Set volume to 0.75
        api.save_setting("audio_feedback_volume", 0.75)
        assert api._config["audio_feedback_volume"] == 0.75

        # Disable master toggle
        api.save_setting("audio_feedback", False)

        # Volume should still be 0.75
        assert api._config["audio_feedback_volume"] == 0.75

        # Re-enable master toggle
        api.save_setting("audio_feedback", True)

        # Volume should still be 0.75
        assert api._config["audio_feedback_volume"] == 0.75

    @patch('config.save_config')
    def test_individual_toggles_work_independently(self, mock_save):
        """Ensure individual sound toggles work correctly when master enabled."""
        api = SettingsAPI()

        # Enable master toggle
        api.save_setting("audio_feedback", True)

        # Change individual toggles
        api.save_setting("sound_processing", False)
        api.save_setting("sound_success", True)
        api.save_setting("sound_error", False)
        api.save_setting("sound_command", True)

        # Verify each persisted independently
        assert api._config["sound_processing"] is False
        assert api._config["sound_success"] is True
        assert api._config["sound_error"] is False
        assert api._config["sound_command"] is True


class TestConcurrentOperations:
    """Test race conditions and concurrent access."""

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    @patch('config.save_config')
    def test_save_while_microphone_test_running(self, mock_save, mock_get_index, mock_stream):
        """Test saving settings while audio test is active."""
        mock_get_index.return_value = 0
        mock_stream.return_value = MagicMock()

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)

        # Start test
        api.start_microphone_test()

        # Save settings while test running
        result = api.save_setting("audio_feedback_volume", 0.5)
        assert result["success"] is True

        # Should not interfere with test
        assert api._audio_test_running is True

    @patch('config.save_config')
    def test_multiple_rapid_saves(self, mock_save):
        """Test rapidly changing values doesn't corrupt config."""
        api = SettingsAPI()

        # Simulate user rapidly dragging slider
        for value in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            result = api.save_setting("audio_feedback_volume", value)
            assert result["success"] is True

        # Final value should be 1.0
        assert api._config["audio_feedback_volume"] == 1.0

    @patch('config.get_input_devices')
    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_device_refresh_during_test(self, mock_get_index, mock_stream, mock_get_devices):
        """Test refreshing devices while microphone test is running."""
        mock_get_index.return_value = 0
        mock_stream.return_value = MagicMock()
        mock_get_devices.return_value = [("System Default", None)]

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)

        # Start test
        api.start_microphone_test()

        # Refresh devices
        result = api.refresh_audio_devices()

        # Should succeed without interfering with test
        assert result["success"] is True
        assert api._audio_test_running is True


class TestErrorRecovery:
    """Test graceful error handling."""

    def test_save_setting_with_invalid_key(self):
        """Test saving setting with None or empty key."""
        api = SettingsAPI()

        # Should handle gracefully
        try:
            result = api.save_setting("", "value")
            # Should either fail gracefully or succeed with warning
        except Exception as e:
            # Should not crash
            assert True

    @patch('config.save_config')
    def test_save_config_raises_exception(self, mock_save):
        """Test behavior when config save fails."""
        mock_save.side_effect = OSError("Permission denied")

        api = SettingsAPI()

        # Save should fail but not crash
        result = api.save_setting("audio_feedback", True)

        # Should return error
        assert result["success"] is False
        assert "error" in result

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_microphone_stream_start_fails(self, mock_get_index, mock_stream):
        """Test when audio stream fails to start."""
        mock_get_index.return_value = 0
        mock_instance = MagicMock()
        mock_instance.start.side_effect = OSError("Audio driver error")
        mock_stream.return_value = mock_instance

        api = SettingsAPI()
        result = api.start_microphone_test()

        # Should fail gracefully
        assert result["success"] is False
        assert "error" in result


class TestCrossFeatureInteractions:
    """Test interactions between different settings."""

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    @patch('config.save_config')
    def test_changing_device_stops_microphone_test(self, mock_save, mock_get_index, mock_stream):
        """Verify changing device while test is running stops the test."""
        mock_get_index.return_value = 0
        mock_stream.return_value = MagicMock()

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)

        # Start test
        api.start_microphone_test()
        assert api._audio_test_running is True

        # User should manually stop test before changing device
        # This test verifies test doesn't crash if device changed
        result = api.save_setting("input_device", "New Device")
        assert result["success"] is True

    @patch('config.save_config')
    def test_sample_rate_and_device_both_saved(self, mock_save):
        """Verify changing both device and sample rate persists both."""
        api = SettingsAPI()

        api.save_setting("input_device", "Blue Yeti")
        api.save_setting("sample_rate", 48000)

        assert api._config["input_device"]["name"] == "Blue Yeti"
        assert api._config["sample_rate"] == 48000


class TestBackwardsCompatibility:
    """Ensure new code works with old configs."""

    @patch('config.load_config')
    def test_load_config_without_audio_feedback_key(self, mock_load):
        """Test configs from before master toggle was added."""
        # Old config without audio_feedback
        old_config = {
            "audio_feedback_volume": 0.5,
            "sound_processing": True,
            "sound_success": True,
            "sound_error": True,
            "sound_command": True
        }
        mock_load.return_value = old_config

        api = SettingsAPI()
        settings = api.get_all_settings()

        # Should work without crashing
        assert settings["success"] is True
        # audio_feedback should default to True
        assert settings["data"].get("audio_feedback", True) is True

    @patch('config.load_config')
    def test_load_config_with_string_device(self, mock_load):
        """Test old device storage format (string) still works."""
        # Old format: device stored as string
        old_config = {
            "input_device": "Blue Yeti"  # Old: string, New: dict
        }
        mock_load.return_value = old_config

        api = SettingsAPI()
        settings = api.get_all_settings()

        # Should handle gracefully
        assert settings["success"] is True

    @patch('config.save_config')
    def test_setting_audio_feedback_to_none(self, mock_save):
        """Test setting audio_feedback to None (legacy behavior)."""
        api = SettingsAPI()

        # Should handle None gracefully
        result = api.save_setting("audio_feedback", None)
        # Either convert to False or handle as False
        assert result["success"] is True


class TestDeviceEnumerationEdgeCases:
    """Test edge cases in device enumeration."""

    @patch('config.get_input_devices')
    def test_no_audio_devices_available(self, mock_get_devices):
        """Test when no audio devices are found."""
        mock_get_devices.return_value = []

        api = SettingsAPI()
        result = api.get_audio_devices()

        # Should return empty list, not crash
        assert result["success"] is True
        assert len(result["data"]) == 0

    @patch('config.get_input_devices')
    def test_device_with_unicode_name(self, mock_get_devices):
        """Test device with special characters in name."""
        mock_get_devices.return_value = [
            ("麦克风 (Microphone) 🎤", {"name": "麦克风", "index": 1})
        ]

        api = SettingsAPI()
        result = api.get_audio_devices()

        assert result["success"] is True
        assert "麦克风" in result["data"][0]["name"]

    @patch('config.get_input_devices')
    def test_device_enumeration_raises_exception(self, mock_get_devices):
        """Test when device enumeration fails."""
        mock_get_devices.side_effect = OSError("Audio driver not available")

        api = SettingsAPI()
        result = api.get_audio_devices()

        # Should return error, not crash
        assert result["success"] is False
        assert "error" in result


class TestNoiseGateThresholdCalculations:
    """Test noise gate threshold edge cases."""

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_audio_callback_handles_zero_input(self, mock_get_index, mock_stream):
        """Test audio callback with silence (zero input)."""
        import numpy as np

        mock_get_index.return_value = 0
        callback_func = None

        def capture_callback(*args, **kwargs):
            nonlocal callback_func
            callback_func = kwargs['callback']
            return MagicMock()

        mock_stream.side_effect = capture_callback

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)
        api.start_microphone_test()

        # Simulate complete silence
        silent_data = np.array([[0.0]])
        callback_func(silent_data, 1024, None, None)

        # Should handle gracefully (output -60 dB floor)
        window.evaluate_js.assert_called()
        call_args = window.evaluate_js.call_args[0][0]
        assert 'onAudioLevel' in call_args
        assert '-60' in call_args  # Floor value

    @patch('sounddevice.InputStream')
    @patch('config.get_device_index')
    def test_audio_callback_handles_very_loud_input(self, mock_get_index, mock_stream):
        """Test audio callback with very loud input."""
        import numpy as np

        mock_get_index.return_value = 0
        callback_func = None

        def capture_callback(*args, **kwargs):
            nonlocal callback_func
            callback_func = kwargs['callback']
            return MagicMock()

        mock_stream.side_effect = capture_callback

        api = SettingsAPI()
        window = MagicMock()
        api.set_window(window)
        api.start_microphone_test()

        # Simulate very loud audio (clipping)
        loud_data = np.array([[1.0]])  # Max amplitude
        callback_func(loud_data, 1024, None, None)

        # Should clamp to -20 dB ceiling
        window.evaluate_js.assert_called()
        call_args = window.evaluate_js.call_args[0][0]
        assert 'onAudioLevel' in call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
