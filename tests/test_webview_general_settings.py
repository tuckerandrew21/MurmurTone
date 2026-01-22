"""
Tests for PyWebView General settings page feature parity.
Verifies Output and Preview Window sections work correctly.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_webview import SettingsAPI
import config


class TestOutputSettings:
    """Test Output section settings (auto_paste, paste_mode)."""

    def test_auto_paste_loads_from_config(self):
        """Verify auto_paste setting loads correctly."""
        with patch('config.load_config') as mock_load:
            mock_load.return_value = {**config.DEFAULTS, "auto_paste": False}
            api = SettingsAPI()

            result = api.get_all_settings()

            assert result["success"] is True
            assert result["data"]["auto_paste"] is False

    def test_auto_paste_saves_correctly(self):
        """Verify auto_paste setting saves correctly."""
        api = SettingsAPI()

        result = api.save_setting("auto_paste", False)

        assert result["success"] is True
        assert api._config["auto_paste"] is False

    def test_paste_mode_valid_values(self):
        """Verify paste_mode accepts valid values (clipboard and direct, NOT type)."""
        api = SettingsAPI()

        # Test both valid modes
        for mode in ["clipboard", "direct"]:
            result = api.save_setting("paste_mode", mode)
            assert result["success"] is True, f"Failed to save {mode}"
            assert api._config["paste_mode"] == mode

    def test_paste_mode_defaults_to_clipboard(self):
        """Verify paste_mode defaults to clipboard."""
        with patch('config.load_config') as mock_load:
            # Return only defaults without any user overrides
            mock_load.return_value = config.DEFAULTS.copy()
            api = SettingsAPI()

            result = api.get_all_settings()

            # Should use DEFAULTS from config.py which is "clipboard"
            assert result["data"]["paste_mode"] == "clipboard"


class TestPreviewWindowSettings:
    """Test Preview Window section settings."""

    def test_preview_enabled_loads_from_config(self):
        """Verify preview_enabled setting loads correctly."""
        with patch('config.load_config') as mock_load:
            mock_load.return_value = {**config.DEFAULTS, "preview_enabled": False}
            api = SettingsAPI()

            result = api.get_all_settings()

            assert result["success"] is True
            assert result["data"]["preview_enabled"] is False

    def test_preview_position_valid_values(self):
        """Verify preview_position accepts all 5 valid values."""
        api = SettingsAPI()

        positions = ["bottom_right", "bottom_left", "top_right", "top_left", "center"]
        for pos in positions:
            result = api.save_setting("preview_position", pos)
            assert result["success"] is True, f"Failed to save position {pos}"
            assert api._config["preview_position"] == pos

    def test_preview_theme_valid_values(self):
        """Verify preview_theme accepts valid values (dark and light)."""
        api = SettingsAPI()

        for theme in ["dark", "light"]:
            result = api.save_setting("preview_theme", theme)
            assert result["success"] is True, f"Failed to save theme {theme}"
            assert api._config["preview_theme"] == theme

    def test_preview_auto_hide_delay_validation(self):
        """Verify preview_auto_hide_delay is validated and clamped to range."""
        api = SettingsAPI()

        # Valid range: 0-10 seconds (per validator in settings_webview.py)
        result = api.save_setting("preview_auto_hide_delay", 5.0)
        assert result["success"] is True
        assert api._config["preview_auto_hide_delay"] == 5.0

    def test_preview_auto_hide_delay_clamps_to_range(self):
        """Verify preview_auto_hide_delay clamps out-of-range values."""
        api = SettingsAPI()

        # Test values beyond range - should be clamped by validator
        result = api.save_setting("preview_auto_hide_delay", -1.0)
        assert result["success"] is True
        # Should be clamped to minimum (0.0)
        assert api._config["preview_auto_hide_delay"] >= 0.0

        result = api.save_setting("preview_auto_hide_delay", 20.0)
        assert result["success"] is True
        # Should be clamped to maximum (10.0)
        assert api._config["preview_auto_hide_delay"] <= 10.0

    def test_preview_font_size_validation(self):
        """Verify preview_font_size accepts valid range (8-18)."""
        api = SettingsAPI()

        # Test valid range
        for size in [8, 11, 14, 18]:
            result = api.save_setting("preview_font_size", size)
            assert result["success"] is True, f"Failed to save font size {size}"
            assert api._config["preview_font_size"] == size

    def test_preview_font_size_accepts_boundary_values(self):
        """Verify preview_font_size accepts boundary values."""
        api = SettingsAPI()

        # Test minimum
        result = api.save_setting("preview_font_size", 8)
        assert result["success"] is True
        assert api._config["preview_font_size"] == 8

        # Test maximum
        result = api.save_setting("preview_font_size", 18)
        assert result["success"] is True
        assert api._config["preview_font_size"] == 18


class TestFeatureParity:
    """Test that PyWebView matches Tkinter functionality."""

    def test_all_general_settings_exist_in_config(self):
        """Verify all General page settings exist in config DEFAULTS."""
        required_settings = [
            "hotkey",
            "recording_mode",
            "language",
            "auto_paste",
            "paste_mode",
            "preview_enabled",
            "preview_position",
            "preview_theme",
            "preview_auto_hide_delay",
            "preview_font_size",
            "start_with_windows"
        ]

        for setting in required_settings:
            assert setting in config.DEFAULTS, f"Missing {setting} in DEFAULTS"

    def test_webview_api_returns_all_general_settings(self):
        """Verify get_all_settings returns all General page settings."""
        api = SettingsAPI()

        result = api.get_all_settings()

        assert result["success"] is True
        data = result["data"]

        # Check all General page settings are present
        assert "hotkey" in data
        assert "recording_mode" in data
        assert "language" in data
        assert "auto_paste" in data
        assert "paste_mode" in data
        assert "preview_enabled" in data
        assert "preview_position" in data
        assert "preview_theme" in data
        assert "preview_auto_hide_delay" in data
        assert "preview_font_size" in data
        assert "start_with_windows" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
