"""
Tests for settings GUI bindings - verifies all settings save and load correctly.

These tests verify the GUI ↔ config round-trip without launching actual GUI windows.
"""
import pytest
import json
import os
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import settings_logic


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config file for testing."""
    config_file = tmp_path / "settings.json"
    # Start with defaults
    with open(config_file, "w") as f:
        json.dump(config.DEFAULTS.copy(), f)
    return config_file


@pytest.fixture
def mock_config_path(tmp_path, monkeypatch):
    """Mock config path to use temp directory."""
    config_file = tmp_path / "settings.json"
    monkeypatch.setattr(config, "get_config_path", lambda: str(config_file))
    return config_file


# =============================================================================
# Label Conversion Tests
# =============================================================================

class TestLanguageConversions:
    """Test language code ↔ label conversions."""

    def test_code_to_label_english(self):
        assert settings_logic.language_code_to_label("en") == "English"

    def test_code_to_label_auto(self):
        assert settings_logic.language_code_to_label("auto") == "Auto-detect"

    def test_code_to_label_unknown(self):
        # Unknown codes return as-is
        assert settings_logic.language_code_to_label("xx") == "xx"

    def test_label_to_code_english(self):
        assert settings_logic.language_label_to_code("English") == "en"

    def test_label_to_code_auto(self):
        assert settings_logic.language_label_to_code("Auto-detect") == "auto"

    def test_label_to_code_unknown(self):
        # Unknown labels return as-is
        assert settings_logic.language_label_to_code("Unknown") == "Unknown"

    def test_round_trip_all_languages(self):
        """All language codes should round-trip correctly."""
        for code in config.LANGUAGE_OPTIONS:
            label = settings_logic.language_code_to_label(code)
            back_to_code = settings_logic.language_label_to_code(label)
            assert back_to_code == code, f"Round-trip failed for {code}"


class TestProcessingModeConversions:
    """Test processing mode code ↔ label conversions."""

    def test_code_to_label_auto(self):
        assert settings_logic.processing_mode_code_to_label("auto") == "Auto"

    def test_code_to_label_cpu(self):
        assert settings_logic.processing_mode_code_to_label("cpu") == "CPU"

    def test_code_to_label_gpu_balanced(self):
        assert settings_logic.processing_mode_code_to_label("gpu-balanced") == "GPU - Balanced"

    def test_code_to_label_gpu_quality(self):
        assert settings_logic.processing_mode_code_to_label("gpu-quality") == "GPU - Quality"

    def test_label_to_code_auto(self):
        assert settings_logic.processing_mode_label_to_code("Auto") == "auto"

    def test_label_to_code_cpu(self):
        assert settings_logic.processing_mode_label_to_code("CPU") == "cpu"

    def test_label_to_code_gpu_balanced(self):
        assert settings_logic.processing_mode_label_to_code("GPU - Balanced") == "gpu-balanced"

    def test_round_trip_all_modes(self):
        """All processing modes should round-trip correctly."""
        for code in config.PROCESSING_MODE_OPTIONS:
            label = settings_logic.processing_mode_code_to_label(code)
            back_to_code = settings_logic.processing_mode_label_to_code(label)
            assert back_to_code == code, f"Round-trip failed for {code}"


class TestRecordingModeConversions:
    """Test recording mode mappings from settings_gui.py."""

    def test_recording_mode_labels_defined(self):
        import settings_gui
        assert "push_to_talk" in settings_gui.RECORDING_MODE_LABELS
        assert "toggle" in settings_gui.RECORDING_MODE_LABELS
        assert "auto_stop" in settings_gui.RECORDING_MODE_LABELS

    def test_recording_mode_values_reverse(self):
        import settings_gui
        # VALUES should be reverse of LABELS
        for code, label in settings_gui.RECORDING_MODE_LABELS.items():
            assert settings_gui.RECORDING_MODE_VALUES[label] == code


class TestPasteModeConversions:
    """Test paste mode mappings from settings_gui.py."""

    def test_paste_mode_labels_defined(self):
        import settings_gui
        assert "clipboard" in settings_gui.PASTE_MODE_LABELS
        assert "type" in settings_gui.PASTE_MODE_LABELS

    def test_paste_mode_values_reverse(self):
        import settings_gui
        for code, label in settings_gui.PASTE_MODE_LABELS.items():
            assert settings_gui.PASTE_MODE_VALUES[label] == code


class TestPreviewPositionConversions:
    """Test preview position mappings from settings_gui.py."""

    def test_preview_position_labels_defined(self):
        import settings_gui
        expected = ["top_left", "top_right", "bottom_left", "bottom_right", "center"]
        for pos in expected:
            assert pos in settings_gui.PREVIEW_POSITION_LABELS

    def test_preview_position_values_reverse(self):
        import settings_gui
        for code, label in settings_gui.PREVIEW_POSITION_LABELS.items():
            assert settings_gui.PREVIEW_POSITION_VALUES[label] == code


class TestPreviewThemeConversions:
    """Test preview theme mappings from settings_gui.py."""

    def test_preview_theme_labels_defined(self):
        import settings_gui
        assert "dark" in settings_gui.PREVIEW_THEME_LABELS
        assert "light" in settings_gui.PREVIEW_THEME_LABELS

    def test_preview_theme_values_reverse(self):
        import settings_gui
        for code, label in settings_gui.PREVIEW_THEME_LABELS.items():
            assert settings_gui.PREVIEW_THEME_VALUES[label] == code


class TestSampleRateOptions:
    """Test sample rate options from settings_gui.py."""

    def test_sample_rate_options_defined(self):
        import settings_gui
        assert 16000 in settings_gui.SAMPLE_RATE_OPTIONS
        assert 44100 in settings_gui.SAMPLE_RATE_OPTIONS
        assert 48000 in settings_gui.SAMPLE_RATE_OPTIONS


# =============================================================================
# Validation Tests
# =============================================================================

class TestSampleRateValidation:
    """Test sample rate validation."""

    def test_valid_rate_16000(self):
        assert settings_logic.validate_sample_rate(16000) == 16000

    def test_valid_rate_44100(self):
        assert settings_logic.validate_sample_rate(44100) == 44100

    def test_valid_rate_48000(self):
        assert settings_logic.validate_sample_rate(48000) == 48000

    def test_valid_rate_string(self):
        assert settings_logic.validate_sample_rate("16000") == 16000

    def test_invalid_rate_returns_default(self):
        assert settings_logic.validate_sample_rate(12345) == 16000

    def test_invalid_string_returns_default(self):
        assert settings_logic.validate_sample_rate("invalid") == 16000

    def test_none_returns_default(self):
        assert settings_logic.validate_sample_rate(None) == 16000


class TestSilenceDurationValidation:
    """Test silence duration validation."""

    def test_valid_duration(self):
        assert settings_logic.validate_silence_duration(2.0) == 2.0

    def test_string_duration(self):
        assert settings_logic.validate_silence_duration("3.5") == 3.5

    def test_below_minimum_clamped(self):
        assert settings_logic.validate_silence_duration(0.1) == 0.5

    def test_above_maximum_clamped(self):
        assert settings_logic.validate_silence_duration(15.0) == 10.0

    def test_invalid_returns_default(self):
        assert settings_logic.validate_silence_duration("invalid") == 2.0

    def test_none_returns_default(self):
        assert settings_logic.validate_silence_duration(None) == 2.0


class TestVolumeValidation:
    """Test volume validation."""

    def test_valid_volume(self):
        assert settings_logic.validate_volume(50) == 50

    def test_below_minimum_clamped(self):
        assert settings_logic.validate_volume(-10) == 0

    def test_above_maximum_clamped(self):
        assert settings_logic.validate_volume(150) == 100

    def test_string_volume(self):
        assert settings_logic.validate_volume("75") == 75

    def test_invalid_returns_default(self):
        assert settings_logic.validate_volume("invalid") == 100


class TestNoiseThresholdValidation:
    """Test noise threshold validation."""

    def test_valid_threshold(self):
        assert settings_logic.validate_noise_threshold(-40) == -40

    def test_below_minimum_clamped(self):
        assert settings_logic.validate_noise_threshold(-80) == -60

    def test_above_maximum_clamped(self):
        assert settings_logic.validate_noise_threshold(-10) == -20

    def test_invalid_returns_default(self):
        assert settings_logic.validate_noise_threshold("invalid") == -40


class TestPreviewDelayValidation:
    """Test preview delay validation."""

    def test_valid_delay(self):
        assert settings_logic.validate_preview_delay(2.5) == 2.5

    def test_zero_delay_allowed(self):
        assert settings_logic.validate_preview_delay(0.0) == 0.0

    def test_below_minimum_clamped(self):
        assert settings_logic.validate_preview_delay(-1.0) == 0.0

    def test_above_maximum_clamped(self):
        assert settings_logic.validate_preview_delay(15.0) == 10.0

    def test_string_delay(self):
        assert settings_logic.validate_preview_delay("3.0") == 3.0


# =============================================================================
# Audio Meter Helper Tests
# =============================================================================

class TestDbConversions:
    """Test dB ↔ linear conversions."""

    def test_db_to_linear_min(self):
        # -60 dB should map to 0.0
        assert settings_logic.db_to_linear(-60, min_db=-60, max_db=-20) == 0.0

    def test_db_to_linear_max(self):
        # -20 dB should map to 1.0
        assert settings_logic.db_to_linear(-20, min_db=-60, max_db=-20) == 1.0

    def test_db_to_linear_mid(self):
        # -40 dB should map to 0.5
        assert settings_logic.db_to_linear(-40, min_db=-60, max_db=-20) == 0.5

    def test_linear_to_db_min(self):
        assert settings_logic.linear_to_db(0.0, min_db=-60, max_db=-20) == -60

    def test_linear_to_db_max(self):
        assert settings_logic.linear_to_db(1.0, min_db=-60, max_db=-20) == -20

    def test_linear_to_db_mid(self):
        assert settings_logic.linear_to_db(0.5, min_db=-60, max_db=-20) == -40

    def test_round_trip(self):
        """dB → linear → dB should round-trip."""
        for db in [-60, -50, -40, -30, -20]:
            linear = settings_logic.db_to_linear(db, min_db=-60, max_db=-20)
            back = settings_logic.linear_to_db(linear, min_db=-60, max_db=-20)
            assert back == db


class TestRmsToDb:
    """Test RMS to dB conversion."""

    def test_rms_to_db_unity(self):
        # RMS of 1.0 should be 0 dB
        assert settings_logic.rms_to_db(1.0) == 0.0

    def test_rms_to_db_zero(self):
        # RMS of 0 should return floor
        assert settings_logic.rms_to_db(0.0) == -60

    def test_rms_to_db_negative(self):
        # Negative values should return floor
        assert settings_logic.rms_to_db(-0.5) == -60

    def test_rms_to_db_small(self):
        # Small RMS should give large negative dB
        import math
        result = settings_logic.rms_to_db(0.001)
        expected = 20 * math.log10(0.001)
        assert result == pytest.approx(expected, rel=0.01)


# =============================================================================
# Config Save/Load Tests
# =============================================================================

class TestConfigPersistence:
    """Test that config saves and loads correctly."""

    def test_save_and_load_preserves_values(self, mock_config_path):
        """Save then load should return same values."""
        test_config = config.DEFAULTS.copy()
        test_config["model_size"] = "base.en"
        test_config["language"] = "es"
        test_config["audio_feedback"] = False

        config.save_config(test_config)
        loaded = config.load_config()

        assert loaded["model_size"] == "base.en"
        assert loaded["language"] == "es"
        assert loaded["audio_feedback"] is False

    def test_load_missing_file_returns_defaults(self, tmp_path, monkeypatch):
        """Loading nonexistent config should return defaults."""
        nonexistent = tmp_path / "nonexistent.json"
        monkeypatch.setattr(config, "get_config_path", lambda: str(nonexistent))

        loaded = config.load_config()
        assert loaded == config.DEFAULTS

    def test_save_to_existing_directory_works(self, mock_config_path):
        """Save should work when parent directory exists."""
        config.save_config({"model_size": "tiny.en"})
        assert mock_config_path.exists()


class TestBooleanSettings:
    """Test boolean settings save/load correctly."""

    boolean_keys = [
        "audio_feedback",
        "auto_paste",
        "start_with_windows",
        "voice_commands_enabled",
        "scratch_that_enabled",
        "filler_removal_enabled",
        "filler_removal_aggressive",
        "preview_enabled",
        "noise_gate_enabled",
        "sound_processing",
        "sound_success",
        "sound_error",
        "sound_command",
        "translation_enabled",
        "ai_cleanup_enabled",
    ]

    @pytest.mark.parametrize("key", boolean_keys)
    def test_boolean_true_saves_correctly(self, mock_config_path, key):
        """Boolean True should save and load as True."""
        test_config = config.DEFAULTS.copy()
        test_config[key] = True
        config.save_config(test_config)

        loaded = config.load_config()
        assert loaded[key] is True, f"{key} should be True"

    @pytest.mark.parametrize("key", boolean_keys)
    def test_boolean_false_saves_correctly(self, mock_config_path, key):
        """Boolean False should save and load as False."""
        test_config = config.DEFAULTS.copy()
        test_config[key] = False
        config.save_config(test_config)

        loaded = config.load_config()
        assert loaded[key] is False, f"{key} should be False"


class TestStringSettings:
    """Test string settings save/load correctly."""

    string_settings = [
        ("model_size", "medium.en"),
        ("language", "fr"),
        ("recording_mode", "auto_stop"),
        ("paste_mode", "type"),
        ("processing_mode", "gpu-quality"),
        ("preview_position", "top-left"),
        ("preview_theme", "light"),
        ("ai_cleanup_mode", "formality"),
        ("ai_formality_level", "formal"),
        ("ollama_model", "mistral:7b"),
    ]

    @pytest.mark.parametrize("key,value", string_settings)
    def test_string_saves_correctly(self, mock_config_path, key, value):
        """String values should save and load correctly."""
        test_config = config.DEFAULTS.copy()
        test_config[key] = value
        config.save_config(test_config)

        loaded = config.load_config()
        assert loaded[key] == value, f"{key} should be {value}"


class TestNumericSettings:
    """Test numeric settings save/load correctly."""

    numeric_settings = [
        ("sample_rate", 48000),
        ("silence_duration_sec", 3.5),
        ("noise_gate_threshold_db", -35),
        ("preview_auto_hide_delay", 5.0),
        ("preview_font_size", 14),
    ]

    @pytest.mark.parametrize("key,value", numeric_settings)
    def test_numeric_saves_correctly(self, mock_config_path, key, value):
        """Numeric values should save and load correctly."""
        test_config = config.DEFAULTS.copy()
        test_config[key] = value
        config.save_config(test_config)

        loaded = config.load_config()
        assert loaded[key] == value, f"{key} should be {value}"


class TestListAndDictSettings:
    """Test list and dict settings save/load correctly."""

    def test_custom_dictionary_saves(self, mock_config_path):
        """Custom dictionary list should save correctly."""
        test_config = config.DEFAULTS.copy()
        test_config["custom_dictionary"] = [
            {"from": "teh", "to": "the", "case_sensitive": False},
            {"from": "recieve", "to": "receive", "case_sensitive": False},
        ]
        config.save_config(test_config)

        loaded = config.load_config()
        assert len(loaded["custom_dictionary"]) == 2
        assert loaded["custom_dictionary"][0]["from"] == "teh"

    def test_custom_vocabulary_saves(self, mock_config_path):
        """Custom vocabulary list should save correctly."""
        test_config = config.DEFAULTS.copy()
        test_config["custom_vocabulary"] = ["TensorFlow", "Kubernetes", "OpenAI"]
        config.save_config(test_config)

        loaded = config.load_config()
        assert "TensorFlow" in loaded["custom_vocabulary"]
        assert len(loaded["custom_vocabulary"]) == 3

    def test_custom_commands_saves(self, mock_config_path):
        """Custom commands list should save correctly."""
        test_config = config.DEFAULTS.copy()
        test_config["custom_commands"] = [
            {"trigger": "sign off", "replacement": "Best regards,\nJohn", "enabled": True},
        ]
        config.save_config(test_config)

        loaded = config.load_config()
        assert len(loaded["custom_commands"]) == 1
        assert loaded["custom_commands"][0]["trigger"] == "sign off"

    def test_hotkey_dict_saves(self, mock_config_path):
        """Hotkey dictionary should save correctly."""
        test_config = config.DEFAULTS.copy()
        test_config["hotkey"] = {
            "ctrl": False,
            "shift": True,
            "alt": True,
            "key": "f5"
        }
        config.save_config(test_config)

        loaded = config.load_config()
        assert loaded["hotkey"]["ctrl"] is False
        assert loaded["hotkey"]["shift"] is True
        assert loaded["hotkey"]["alt"] is True
        assert loaded["hotkey"]["key"] == "f5"


# =============================================================================
# Defaults Tests
# =============================================================================

class TestDefaults:
    """Test that defaults are properly defined."""

    def test_get_defaults_returns_copy(self):
        """get_defaults() should return a copy, not the original."""
        defaults1 = settings_logic.get_defaults()
        defaults2 = settings_logic.get_defaults()

        defaults1["model_size"] = "modified"
        assert defaults2["model_size"] != "modified"

    def test_defaults_has_all_required_keys(self):
        """DEFAULTS should have all expected keys."""
        defaults = config.DEFAULTS

        required_keys = [
            "model_size", "sample_rate", "language", "hotkey",
            "recording_mode", "silence_duration_sec", "audio_feedback",
            "auto_paste", "paste_mode", "preview_enabled", "preview_position",
            "preview_theme", "preview_auto_hide_delay", "preview_font_size",
            "processing_mode", "noise_gate_enabled", "noise_gate_threshold_db",
            "voice_commands_enabled", "scratch_that_enabled",
            "filler_removal_enabled", "filler_removal_aggressive",
            "ai_cleanup_enabled", "ai_cleanup_mode", "ai_formality_level",
            "ollama_model", "ollama_url",
        ]

        for key in required_keys:
            assert key in defaults, f"Missing default key: {key}"


# =============================================================================
# Integration Tests
# =============================================================================

class TestSettingsBuildDict:
    """Test the build_settings_dict function."""

    def test_build_settings_dict_creates_valid_dict(self):
        """build_settings_dict should create a complete settings dict."""
        result = settings_logic.build_settings_dict(
            model_size="base.en",
            language="en",
            translation_enabled=False,
            translation_source_language="auto",
            sample_rate=16000,
            hotkey={"ctrl": True, "shift": True, "alt": False, "key": "space"},
            recording_mode="push_to_talk",
            silence_duration=2.0,
            audio_feedback=True,
            input_device=None,
            auto_paste=True,
            paste_mode="clipboard",
            start_with_windows=False,
            processing_mode="auto",
            noise_gate_enabled=True,
            noise_gate_threshold_db=-40,
            audio_feedback_volume=100,
            sound_processing=True,
            sound_success=True,
            sound_error=True,
            sound_command=True,
            voice_commands_enabled=True,
            scratch_that_enabled=True,
            filler_removal_enabled=True,
            filler_removal_aggressive=False,
            custom_fillers=[],
            custom_dictionary=[],
            custom_vocabulary=[],
            custom_commands=[],
            ai_cleanup_enabled=False,
            ai_cleanup_mode="grammar",
            ai_formality_level="professional",
            ollama_model="llama3.2:3b",
            ollama_url="http://localhost:11434",
            preview_enabled=True,
            preview_position="bottom_right",
            preview_auto_hide_delay=2.0,
            preview_theme="dark",
            preview_font_size=11,
        )

        assert result["model_size"] == "base.en"
        assert result["language"] == "en"
        assert result["sample_rate"] == 16000
        assert result["preview_enabled"] is True
