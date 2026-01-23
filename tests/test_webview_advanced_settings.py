"""
Integration tests for PyWebView Advanced tab.
Tests verify AI Cleanup, History, and Export functionality.
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_webview import SettingsAPI
import config


class TestAICleanupSettings:
    """Test AI Cleanup configuration on Advanced tab."""

    def test_ai_cleanup_toggle(self):
        """Test enabling/disabling AI cleanup."""
        api = SettingsAPI()

        # Enable AI cleanup
        result = api.save_setting("ai_cleanup_enabled", True)
        assert result["success"] is True

        # Verify setting persisted
        all_settings = api.get_all_settings()
        assert all_settings["data"]["ai_cleanup_enabled"] is True

        # Disable AI cleanup
        result = api.save_setting("ai_cleanup_enabled", False)
        assert result["success"] is True
        all_settings = api.get_all_settings()
        assert all_settings["data"]["ai_cleanup_enabled"] is False

    def test_cleanup_mode_values(self):
        """Test all valid cleanup mode values match Tkinter version."""
        api = SettingsAPI()
        valid_modes = ["grammar", "formality", "both"]

        for mode in valid_modes:
            result = api.save_setting("ai_cleanup_mode", mode)
            assert result["success"] is True
            all_settings = api.get_all_settings()
            assert all_settings["data"]["ai_cleanup_mode"] == mode

    def test_cleanup_mode_default(self):
        """Test cleanup mode default is 'grammar'."""
        # Check config.DEFAULTS
        assert config.DEFAULTS.get("ai_cleanup_mode") == "grammar"

    def test_formality_level_values(self):
        """Test all valid formality level values match Tkinter version."""
        api = SettingsAPI()
        valid_levels = ["casual", "professional", "formal"]

        for level in valid_levels:
            result = api.save_setting("ai_formality_level", level)
            assert result["success"] is True
            all_settings = api.get_all_settings()
            assert all_settings["data"]["ai_formality_level"] == level

    def test_formality_level_default(self):
        """Test formality level default is 'professional'."""
        # Check config.DEFAULTS
        assert config.DEFAULTS.get("ai_formality_level") == "professional"

    def test_ollama_url_setting(self):
        """Test Ollama URL configuration."""
        api = SettingsAPI()

        result = api.save_setting("ollama_url", "http://localhost:11434")
        assert result["success"] is True

        all_settings = api.get_all_settings()
        assert all_settings["data"]["ollama_url"] == "http://localhost:11434"

    def test_ollama_model_setting(self):
        """Test Ollama model configuration."""
        api = SettingsAPI()

        result = api.save_setting("ollama_model", "llama3.2:7b")
        assert result["success"] is True

        all_settings = api.get_all_settings()
        assert all_settings["data"]["ollama_model"] == "llama3.2:7b"


class TestOllamaConnection:
    """Test Ollama connection testing functionality."""

    @patch('urllib.request.urlopen')
    def test_ollama_connection_success(self, mock_urlopen):
        """Test successful Ollama connection."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        api = SettingsAPI()
        result = api.test_ollama_connection("http://localhost:11434")

        assert result["success"] is True
        assert result["data"]["connected"] is True

    @patch('urllib.request.urlopen')
    def test_ollama_connection_failure(self, mock_urlopen):
        """Test failed Ollama connection."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        api = SettingsAPI()
        result = api.test_ollama_connection("http://localhost:11434")

        assert result["success"] is True
        assert result["data"]["connected"] is False


class TestHistoryManagement:
    """Test transcription history management."""

    def test_get_history(self):
        """Test getting history returns expected structure."""
        api = SettingsAPI()
        result = api.get_history()

        assert "history" in result
        assert isinstance(result["history"], list)

    def test_get_history_count(self):
        """Test getting history count."""
        api = SettingsAPI()
        result = api.get_history_count()

        assert "count" in result
        assert isinstance(result["count"], int)

    def test_clear_history(self):
        """Test clearing history."""
        api = SettingsAPI()

        # Create a temp history file
        history_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'transcription_history.json'
        )

        # Write test data
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump([{"timestamp": "2024-01-01", "text": "test"}], f)

        try:
            result = api.clear_history()
            assert result["success"] is True

            # Verify file is removed (clear_history removes the file)
            assert not os.path.exists(history_path)
        finally:
            # Clean up if it still exists
            if os.path.exists(history_path):
                os.unlink(history_path)


class TestHistoryExport:
    """Test history export functionality."""

    def test_export_history_txt_format(self):
        """Test TXT export format."""
        api = SettingsAPI()

        # Mock the window for file dialog
        mock_window = MagicMock()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name

        mock_window.create_file_dialog.return_value = temp_path
        api._window = mock_window

        # Mock get_history to return test data
        with patch.object(api, 'get_history', return_value={
            "history": [
                {"timestamp": "2024-01-01T12:00:00", "text": "Test transcription 1"},
                {"timestamp": "2024-01-01T12:01:00", "text": "Test transcription 2"}
            ]
        }):
            result = api.export_history("txt")

        assert result["success"] is True
        assert result["filename"].endswith(".txt")

        # Verify file contents
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Transcription History" in content
            assert "Test transcription 1" in content
            assert "Test transcription 2" in content

        os.unlink(temp_path)

    def test_export_history_csv_format(self):
        """Test CSV export format."""
        api = SettingsAPI()

        mock_window = MagicMock()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name

        mock_window.create_file_dialog.return_value = temp_path
        api._window = mock_window

        with patch.object(api, 'get_history', return_value={
            "history": [
                {"timestamp": "2024-01-01T12:00:00", "text": "Test transcription"},
            ]
        }):
            result = api.export_history("csv")

        assert result["success"] is True
        assert result["filename"].endswith(".csv")

        # Verify CSV structure
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Timestamp,Text,Characters" in content
            assert "Test transcription" in content

        os.unlink(temp_path)

    def test_export_history_json_format(self):
        """Test JSON export format."""
        api = SettingsAPI()

        mock_window = MagicMock()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        mock_window.create_file_dialog.return_value = temp_path
        api._window = mock_window

        with patch.object(api, 'get_history', return_value={
            "history": [
                {"timestamp": "2024-01-01T12:00:00", "text": "Test transcription"},
            ]
        }):
            result = api.export_history("json")

        assert result["success"] is True
        assert result["filename"].endswith(".json")

        # Verify valid JSON
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert data[0]["text"] == "Test transcription"

        os.unlink(temp_path)

    def test_export_history_cancelled(self):
        """Test export cancellation."""
        api = SettingsAPI()

        mock_window = MagicMock()
        mock_window.create_file_dialog.return_value = None
        api._window = mock_window

        result = api.export_history("txt")

        assert result["success"] is False
        assert result.get("cancelled") is True


class TestHTMLDropdownOptions:
    """Test that HTML dropdown options match config.py."""

    def test_cleanup_mode_options_in_html(self):
        """Verify cleanup mode options in HTML match valid values."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for correct values (not 'concise')
        assert 'value="grammar"' in content
        assert 'value="formality"' in content
        assert 'value="both"' in content
        # Ensure old incorrect value is removed
        assert 'value="concise"' not in content

    def test_formality_level_options_in_html(self):
        """Verify formality level options in HTML match valid values."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for correct values
        assert 'value="casual"' in content
        assert 'value="professional"' in content
        assert 'value="formal"' in content
        # Ensure old incorrect value is removed
        assert 'value="neutral"' not in content


class TestJSDefaults:
    """Test that JS defaults match config.py."""

    def test_js_default_cleanup_mode(self):
        """Verify JS default for cleanup mode is 'grammar'."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for correct default
        assert "ai_cleanup_mode ?? 'grammar'" in content

    def test_js_default_formality_level(self):
        """Verify JS default for formality level is 'professional'."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for correct default
        assert "ai_formality_level ?? 'professional'" in content
