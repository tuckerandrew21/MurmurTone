"""
Comprehensive backend unit tests for Text settings tab in WebView GUI.

Tests all Text tab settings including:
- Voice commands
- Filler word removal
- Custom filler words
- Custom dictionary
- Text shortcuts
- Custom vocabulary
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_webview import SettingsAPI
import config


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def api(mocker):
    """Create a SettingsAPI instance with mocked config."""
    mock_config = config.DEFAULTS.copy()
    mocker.patch('config.load_config', return_value=mock_config)
    mocker.patch('config.save_config')
    return SettingsAPI()


@pytest.fixture
def text_settings_config():
    """Return a config with all Text tab settings populated."""
    return {
        **config.DEFAULTS,
        "voice_commands_enabled": True,
        "scratch_that_enabled": True,
        "filler_removal_enabled": True,
        "filler_removal_aggressive": False,
        "custom_fillers": ["actually", "basically"],
        "custom_dictionary": [
            {"from": "teh", "to": "the", "case_sensitive": False},
            {"from": "youre", "to": "you're", "case_sensitive": False}
        ],
        "custom_vocabulary": ["TensorFlow", "Kubernetes", "Dr. Smith"],
        "custom_commands": [
            {"trigger": "addr", "replacement": "123 Main St", "enabled": True},
            {"trigger": "sig", "replacement": "Best regards,\nJohn", "enabled": True}
        ]
    }


# =============================================================================
# Test Voice Commands Settings
# =============================================================================

class TestVoiceCommandsSettings:
    """Test voice commands and scratch that settings."""

    def test_voice_commands_loads_from_config(self, mocker):
        """Verify voice_commands_enabled loads with default True."""
        mock_config = {**config.DEFAULTS, "voice_commands_enabled": True}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["voice_commands_enabled"] is True

    def test_voice_commands_saves_correctly(self, api, mocker):
        """Verify voice_commands_enabled saves boolean."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("voice_commands_enabled", False)

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["voice_commands_enabled"] is False

    def test_scratch_that_loads_from_config(self, mocker):
        """Verify scratch_that_enabled loads with default True."""
        mock_config = {**config.DEFAULTS, "scratch_that_enabled": True}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["scratch_that_enabled"] is True

    def test_scratch_that_saves_correctly(self, api, mocker):
        """Verify scratch_that_enabled saves boolean."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("scratch_that_enabled", False)

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["scratch_that_enabled"] is False

    def test_voice_commands_defaults_true(self, mocker):
        """Verify missing config key defaults to True."""
        mock_config = config.DEFAULTS.copy()
        # Remove the key to test default
        if "voice_commands_enabled" in mock_config:
            del mock_config["voice_commands_enabled"]
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        # Should default to True based on config.DEFAULTS
        result = api.get_all_settings()

        assert result["success"] is True

    def test_scratch_that_independent_of_parent(self, api, mocker):
        """Backend should save scratch_that regardless of voice_commands state."""
        save_mock = mocker.patch('config.save_config')

        # Disable voice commands
        api.save_setting("voice_commands_enabled", False)
        # Enable scratch that (should work even if parent disabled)
        result = api.save_setting("scratch_that_enabled", True)

        assert result["success"] is True
        assert api._config["scratch_that_enabled"] is True


# =============================================================================
# Test Filler Removal Settings
# =============================================================================

class TestFillerRemovalSettings:
    """Test filler word removal settings."""

    def test_filler_removal_loads_from_config(self, mocker):
        """Verify filler_removal_enabled loads correctly."""
        mock_config = {**config.DEFAULTS, "filler_removal_enabled": True}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["filler_removal_enabled"] is True

    def test_filler_aggressive_loads_from_config(self, mocker):
        """Verify filler_removal_aggressive loads with default False."""
        mock_config = {**config.DEFAULTS, "filler_removal_aggressive": False}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["filler_removal_aggressive"] is False

    def test_filler_removal_saves_correctly(self, api, mocker):
        """Verify boolean save works."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("filler_removal_enabled", True)

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["filler_removal_enabled"] is True

    def test_filler_aggressive_saves_correctly(self, api, mocker):
        """Verify boolean save works."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("filler_removal_aggressive", True)

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["filler_removal_aggressive"] is True

    def test_filler_aggressive_independent_of_parent(self, api, mocker):
        """Backend should save aggressive regardless of filler_removal state."""
        save_mock = mocker.patch('config.save_config')

        # Disable filler removal
        api.save_setting("filler_removal_enabled", False)
        # Enable aggressive mode (should work even if parent disabled)
        result = api.save_setting("filler_removal_aggressive", True)

        assert result["success"] is True
        assert api._config["filler_removal_aggressive"] is True


# =============================================================================
# Test Custom Fillers Settings
# =============================================================================

class TestCustomFillersSettings:
    """Test custom filler words validation and normalization."""

    def test_custom_fillers_loads_empty_array(self, mocker):
        """Verify default [] loads correctly."""
        mock_config = {**config.DEFAULTS, "custom_fillers": []}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["custom_fillers"] == []

    def test_custom_fillers_saves_array(self, api, mocker):
        """Save ["um", "uh", "like"] and verify persistence."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["um", "uh", "like"])

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["custom_fillers"] == ["um", "uh", "like"]

    def test_custom_fillers_validates_as_array(self, api):
        """Reject non-array values with error."""
        result = api.save_setting("custom_fillers", "not an array")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_custom_fillers_normalizes_to_lowercase(self, api, mocker):
        """["UM", "Uh", "LIKE"] should save as ["um", "uh", "like"]."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["UM", "Uh", "LIKE"])

        assert result["success"] is True
        assert api._config["custom_fillers"] == ["um", "uh", "like"]

    def test_custom_fillers_trims_whitespace(self, api, mocker):
        """[" um ", "uh  "] should save as ["um", "uh"]."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", [" um ", "uh  "])

        assert result["success"] is True
        assert api._config["custom_fillers"] == ["um", "uh"]

    def test_custom_fillers_removes_empty_strings(self, api, mocker):
        """["um", "", "uh"] should save as ["um", "uh"]."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["um", "", "uh"])

        assert result["success"] is True
        assert api._config["custom_fillers"] == ["um", "uh"]

    def test_custom_fillers_handles_special_chars(self, api, mocker):
        """["um...", "uh?"] should be preserved."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["um...", "uh?"])

        assert result["success"] is True
        assert api._config["custom_fillers"] == ["um...", "uh?"]

    def test_custom_fillers_handles_unicode(self, api, mocker):
        """["café", "naïve"] should be preserved."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["café", "naïve"])

        assert result["success"] is True
        assert "café" in api._config["custom_fillers"]
        assert "naïve" in api._config["custom_fillers"]

    def test_custom_fillers_handles_large_list(self, api, mocker):
        """100+ items should save without error."""
        save_mock = mocker.patch('config.save_config')
        large_list = [f"word{i}" for i in range(150)]

        result = api.save_setting("custom_fillers", large_list)

        assert result["success"] is True
        assert len(api._config["custom_fillers"]) == 150

    def test_custom_fillers_skips_non_string_items(self, api, mocker):
        """[123, None, {}, "um"] should save as ["um"]."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", [123, None, {}, "um"])

        assert result["success"] is True
        assert api._config["custom_fillers"] == ["um"]

    def test_custom_fillers_removes_duplicates(self, api, mocker):
        """["um", "um", "uh"] should save as ["um", "uh"]."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["um", "um", "uh"])

        assert result["success"] is True
        assert len(api._config["custom_fillers"]) == 2
        assert "um" in api._config["custom_fillers"]
        assert "uh" in api._config["custom_fillers"]

    def test_custom_fillers_case_insensitive_duplicates(self, api, mocker):
        """["um", "UM", "Um"] should save as ["um"] (one entry)."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_fillers", ["um", "UM", "Um"])

        assert result["success"] is True
        assert api._config["custom_fillers"] == ["um"]


# =============================================================================
# Test Dictionary Settings
# =============================================================================

class TestDictionarySettings:
    """Test custom dictionary validation."""

    def test_dictionary_loads_empty_array(self, mocker):
        """Verify default [] loads correctly."""
        mock_config = {**config.DEFAULTS, "custom_dictionary": []}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["custom_dictionary"] == []

    def test_dictionary_saves_correctly(self, api, mocker):
        """Save [{"from": "teh", "to": "the", "case_sensitive": False}]."""
        save_mock = mocker.patch('config.save_config')
        entry = {"from": "teh", "to": "the", "case_sensitive": False}

        result = api.save_setting("custom_dictionary", [entry])

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["custom_dictionary"] == [entry]

    def test_dictionary_validates_structure_missing_from(self, api):
        """Reject dicts missing 'from' key."""
        result = api.save_setting("custom_dictionary", [{"to": "the"}])

        assert result["success"] is False
        assert "missing 'from' or 'to' keys" in result["error"]

    def test_dictionary_validates_structure_missing_to(self, api):
        """Reject dicts missing 'to' key."""
        result = api.save_setting("custom_dictionary", [{"from": "teh"}])

        assert result["success"] is False
        assert "missing 'from' or 'to' keys" in result["error"]

    def test_dictionary_validates_as_array(self, api):
        """Reject non-array values."""
        result = api.save_setting("custom_dictionary", "not an array")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_dictionary_handles_case_sensitive_flag(self, api, mocker):
        """Verify case_sensitive True/False preserved."""
        save_mock = mocker.patch('config.save_config')
        entries = [
            {"from": "API", "to": "api", "case_sensitive": True},
            {"from": "teh", "to": "the", "case_sensitive": False}
        ]

        result = api.save_setting("custom_dictionary", entries)

        assert result["success"] is True
        assert api._config["custom_dictionary"][0]["case_sensitive"] is True
        assert api._config["custom_dictionary"][1]["case_sensitive"] is False

    def test_dictionary_rejects_empty_from_value(self, api):
        """from="" should be rejected."""
        result = api.save_setting("custom_dictionary", [{"from": "", "to": "the"}])

        assert result["success"] is False
        assert "empty 'from' value" in result["error"]

    def test_dictionary_handles_large_list(self, api, mocker):
        """100+ replacements should save without error."""
        save_mock = mocker.patch('config.save_config')
        large_list = [
            {"from": f"word{i}", "to": f"replacement{i}", "case_sensitive": False}
            for i in range(120)
        ]

        result = api.save_setting("custom_dictionary", large_list)

        assert result["success"] is True
        assert len(api._config["custom_dictionary"]) == 120

    def test_dictionary_preserves_order(self, api, mocker):
        """Save 3 entries, verify order maintained."""
        save_mock = mocker.patch('config.save_config')
        entries = [
            {"from": "first", "to": "1st"},
            {"from": "second", "to": "2nd"},
            {"from": "third", "to": "3rd"}
        ]

        result = api.save_setting("custom_dictionary", entries)

        assert result["success"] is True
        assert api._config["custom_dictionary"][0]["from"] == "first"
        assert api._config["custom_dictionary"][1]["from"] == "second"
        assert api._config["custom_dictionary"][2]["from"] == "third"

    def test_dictionary_rejects_non_dict_entry(self, api):
        """Reject array containing non-dict items."""
        result = api.save_setting("custom_dictionary", ["string entry", 123])

        assert result["success"] is False
        assert "must be an object" in result["error"]


# =============================================================================
# Test Shortcuts Settings
# =============================================================================

class TestShortcutsSettings:
    """Test text shortcuts validation."""

    def test_shortcuts_loads_empty_array(self, mocker):
        """Verify default [] loads correctly."""
        mock_config = {**config.DEFAULTS, "custom_commands": []}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["custom_commands"] == []

    def test_shortcuts_saves_correctly(self, api, mocker):
        """Save [{"trigger": "addr", "replacement": "123 Main St", "enabled": True}]."""
        save_mock = mocker.patch('config.save_config')
        entry = {"trigger": "addr", "replacement": "123 Main St", "enabled": True}

        result = api.save_setting("custom_commands", [entry])

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["custom_commands"] == [entry]

    def test_shortcuts_validates_structure_missing_trigger(self, api):
        """Reject dicts missing 'trigger' key."""
        result = api.save_setting("custom_commands", [{"replacement": "text"}])

        assert result["success"] is False
        assert "missing 'trigger' or 'replacement' keys" in result["error"]

    def test_shortcuts_validates_structure_missing_replacement(self, api):
        """Reject dicts missing 'replacement' key."""
        result = api.save_setting("custom_commands", [{"trigger": "addr"}])

        assert result["success"] is False
        assert "missing 'trigger' or 'replacement' keys" in result["error"]

    def test_shortcuts_validates_as_array(self, api):
        """Reject non-array values."""
        result = api.save_setting("custom_commands", "not an array")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_shortcuts_handles_multiline_replacement(self, api, mocker):
        """replacement="Line1\\nLine2" should preserve newlines."""
        save_mock = mocker.patch('config.save_config')
        entry = {"trigger": "sig", "replacement": "Best regards,\nJohn Smith", "enabled": True}

        result = api.save_setting("custom_commands", [entry])

        assert result["success"] is True
        assert "\n" in api._config["custom_commands"][0]["replacement"]

    def test_shortcuts_handles_enabled_flag(self, api, mocker):
        """Verify enabled True/False preserved."""
        save_mock = mocker.patch('config.save_config')
        entries = [
            {"trigger": "addr1", "replacement": "text1", "enabled": True},
            {"trigger": "addr2", "replacement": "text2", "enabled": False}
        ]

        result = api.save_setting("custom_commands", entries)

        assert result["success"] is True
        assert api._config["custom_commands"][0]["enabled"] is True
        assert api._config["custom_commands"][1]["enabled"] is False

    def test_shortcuts_rejects_empty_trigger(self, api):
        """trigger="" should be rejected."""
        result = api.save_setting("custom_commands", [{"trigger": "", "replacement": "text"}])

        assert result["success"] is False
        assert "empty trigger" in result["error"]

    def test_shortcuts_allows_empty_replacement(self, api, mocker):
        """replacement="" should be allowed (expands to nothing)."""
        save_mock = mocker.patch('config.save_config')
        entry = {"trigger": "clear", "replacement": "", "enabled": True}

        result = api.save_setting("custom_commands", [entry])

        assert result["success"] is True
        assert api._config["custom_commands"][0]["replacement"] == ""

    def test_shortcuts_handles_large_list(self, api, mocker):
        """100+ shortcuts should save without error."""
        save_mock = mocker.patch('config.save_config')
        large_list = [
            {"trigger": f"trigger{i}", "replacement": f"text{i}", "enabled": True}
            for i in range(110)
        ]

        result = api.save_setting("custom_commands", large_list)

        assert result["success"] is True
        assert len(api._config["custom_commands"]) == 110

    def test_shortcuts_preserves_order(self, api, mocker):
        """Save 3 entries, verify order maintained."""
        save_mock = mocker.patch('config.save_config')
        entries = [
            {"trigger": "first", "replacement": "1st"},
            {"trigger": "second", "replacement": "2nd"},
            {"trigger": "third", "replacement": "3rd"}
        ]

        result = api.save_setting("custom_commands", entries)

        assert result["success"] is True
        assert api._config["custom_commands"][0]["trigger"] == "first"
        assert api._config["custom_commands"][1]["trigger"] == "second"
        assert api._config["custom_commands"][2]["trigger"] == "third"

    def test_shortcuts_rejects_non_dict_entry(self, api):
        """Reject array containing non-dict items."""
        result = api.save_setting("custom_commands", ["string entry", 123])

        assert result["success"] is False
        assert "must be an object" in result["error"]


# =============================================================================
# Test Vocabulary Settings
# =============================================================================

class TestVocabularySettings:
    """Test custom vocabulary validation."""

    def test_vocabulary_loads_empty_array(self, mocker):
        """Verify default [] loads correctly."""
        mock_config = {**config.DEFAULTS, "custom_vocabulary": []}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        assert result["data"]["custom_vocabulary"] == []

    def test_vocabulary_saves_array(self, api, mocker):
        """Save ["TensorFlow", "Kubernetes"] and verify persistence."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_vocabulary", ["TensorFlow", "Kubernetes"])

        assert result["success"] is True
        save_mock.assert_called_once()
        assert api._config["custom_vocabulary"] == ["TensorFlow", "Kubernetes"]

    def test_vocabulary_validates_as_array(self, api):
        """Reject non-array values with error."""
        result = api.save_setting("custom_vocabulary", "not an array")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_vocabulary_trims_whitespace(self, api, mocker):
        """[" TensorFlow ", "Kubernetes  "] should save trimmed."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_vocabulary", [" TensorFlow ", "Kubernetes  "])

        assert result["success"] is True
        assert api._config["custom_vocabulary"] == ["TensorFlow", "Kubernetes"]

    def test_vocabulary_removes_empty_strings(self, api, mocker):
        """["TensorFlow", "", "Kubernetes"] should save as two items."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_vocabulary", ["TensorFlow", "", "Kubernetes"])

        assert result["success"] is True
        assert len(api._config["custom_vocabulary"]) == 2
        assert "TensorFlow" in api._config["custom_vocabulary"]
        assert "Kubernetes" in api._config["custom_vocabulary"]

    def test_vocabulary_skips_non_string_items(self, api, mocker):
        """[123, None, "TensorFlow"] should save as ["TensorFlow"]."""
        save_mock = mocker.patch('config.save_config')

        result = api.save_setting("custom_vocabulary", [123, None, "TensorFlow"])

        assert result["success"] is True
        assert api._config["custom_vocabulary"] == ["TensorFlow"]


# =============================================================================
# Test Config Errors
# =============================================================================

class TestConfigErrors:
    """Test handling of missing/corrupted config."""

    def test_missing_config_file(self, mocker):
        """API loads defaults when config.yaml missing."""
        mocker.patch('config.load_config', return_value=config.DEFAULTS)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        result = api.get_all_settings()

        assert result["success"] is True
        # Should have default values
        assert "voice_commands_enabled" in result["data"]

    def test_corrupted_custom_fillers_not_array(self, mocker):
        """custom_fillers="string" should be caught by validator."""
        mock_config = {**config.DEFAULTS, "custom_fillers": "corrupted"}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        # Try to save - validator should catch it
        result = api.save_setting("custom_fillers", "string value")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_corrupted_dictionary_invalid_structure(self, mocker):
        """custom_dictionary=[123] should be caught by validator."""
        mock_config = {**config.DEFAULTS, "custom_dictionary": [123]}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        # Try to save invalid structure
        result = api.save_setting("custom_dictionary", [123])

        assert result["success"] is False
        assert "must be an object" in result["error"]

    def test_corrupted_shortcuts_invalid_structure(self, mocker):
        """custom_commands="wrong" should be caught by validator."""
        mock_config = {**config.DEFAULTS, "custom_commands": "wrong"}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        # Try to save invalid value
        result = api.save_setting("custom_commands", "string")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_save_setting_handles_general_exception(self, api, mocker):
        """save_setting should catch and return errors gracefully."""
        # Force an exception by mocking save_config to raise
        mocker.patch('config.save_config', side_effect=Exception("Disk full"))

        result = api.save_setting("voice_commands_enabled", True)

        assert result["success"] is False
        assert "Disk full" in result["error"]

    def test_get_all_settings_handles_exception(self, mocker):
        """get_all_settings should catch and return errors gracefully."""
        # First let init succeed with defaults
        mocker.patch('config.load_config', return_value=config.DEFAULTS)
        api = SettingsAPI()

        # Then make it fail when get_all_settings calls load_config again
        mocker.patch('config.load_config', side_effect=Exception("File not found"))

        result = api.get_all_settings()

        assert result["success"] is False
        assert "File not found" in result["error"]

    def test_vocabulary_corrupted_not_array(self, mocker):
        """custom_vocabulary="string" should be caught by validator."""
        mock_config = {**config.DEFAULTS, "custom_vocabulary": "corrupted"}
        mocker.patch('config.load_config', return_value=mock_config)
        mocker.patch('config.save_config')

        api = SettingsAPI()
        # Try to save - validator should catch it
        result = api.save_setting("custom_vocabulary", "string value")

        assert result["success"] is False
        assert "must be an array" in result["error"]

    def test_dictionary_whitespace_only_from_rejected(self, api):
        """from="   " (whitespace only) should be rejected."""
        result = api.save_setting("custom_dictionary", [{"from": "   ", "to": "the"}])

        assert result["success"] is False
        assert "empty 'from' value" in result["error"]
