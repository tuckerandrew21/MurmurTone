"""
Integration tests for PyWebView UI.
These tests verify the complete flow from UI to config.
"""
import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_webview import SettingsAPI
import config


class TestGeneralPageFlow:
    """Test complete user flow on General page."""

    def test_user_changes_output_settings(self):
        """Simulate user changing Output settings."""
        api = SettingsAPI()

        # User toggles auto-paste off
        result = api.save_setting("auto_paste", False)
        assert result["success"] is True

        # User changes paste mode to direct
        result = api.save_setting("paste_mode", "direct")
        assert result["success"] is True

        # Verify both settings persisted
        all_settings = api.get_all_settings()
        assert all_settings["data"]["auto_paste"] is False
        assert all_settings["data"]["paste_mode"] == "direct"

    def test_user_configures_preview_window(self):
        """Simulate user configuring Preview Window."""
        api = SettingsAPI()

        # User enables preview
        result = api.save_setting("preview_enabled", True)
        assert result["success"] is True

        # User changes position
        result = api.save_setting("preview_position", "top_left")
        assert result["success"] is True

        # User changes theme
        result = api.save_setting("preview_theme", "light")
        assert result["success"] is True

        # User adjusts delay
        result = api.save_setting("preview_auto_hide_delay", 5.0)
        assert result["success"] is True

        # User adjusts font size
        result = api.save_setting("preview_font_size", 14)
        assert result["success"] is True

        # Verify all settings persisted
        all_settings = api.get_all_settings()
        data = all_settings["data"]
        assert data["preview_enabled"] is True
        assert data["preview_position"] == "top_left"
        assert data["preview_theme"] == "light"
        assert data["preview_auto_hide_delay"] == 5.0
        assert data["preview_font_size"] == 14


class TestConfigPersistence:
    """Test that settings persist across sessions."""

    @patch('config.save_config')
    @patch('config.load_config')
    def test_settings_persist_to_disk(self, mock_load, mock_save):
        """Verify settings are saved to config file."""
        mock_load.return_value = config.DEFAULTS.copy()

        api = SettingsAPI()

        # Change multiple settings
        api.save_setting("auto_paste", False)
        api.save_setting("preview_position", "center")
        api.save_setting("preview_font_size", 16)

        # Verify save_config was called
        assert mock_save.call_count >= 3, "save_config should be called for each setting change"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
