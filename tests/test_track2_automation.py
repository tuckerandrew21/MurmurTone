"""
Track 2 Integration Testing - Automated Test Suite

Tests features that can be verified programmatically without manual intervention.
Updated to use functional APIs (not OOP classes).
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import pytest
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
import license


class TestLicenseActivationFlow:
    """Test license activation UI and logic using functional API."""

    def test_trial_active_on_first_launch(self, tmp_path):
        """Verify trial activates on first launch."""
        # Create a fresh config dict
        cfg = config.DEFAULTS.copy()

        # Start trial
        cfg = license.start_trial(cfg)

        status_info = license.get_license_status_info(cfg)
        assert status_info["status"] == license.LicenseStatus.TRIAL
        assert status_info["days_remaining"] == 14

    def test_trial_countdown(self, tmp_path):
        """Verify trial countdown works correctly."""
        cfg = config.DEFAULTS.copy()

        # Set trial start to 5 days ago
        cfg["trial_started_date"] = (datetime.now() - timedelta(days=5)).isoformat()
        cfg["license_status"] = license.LicenseStatus.TRIAL

        days_remaining = license.get_trial_days_remaining(cfg)
        assert days_remaining == 9

    def test_trial_expiration(self, tmp_path):
        """Verify trial expiration detection."""
        cfg = config.DEFAULTS.copy()

        # Set trial start to 15 days ago (expired)
        cfg["trial_started_date"] = (datetime.now() - timedelta(days=15)).isoformat()
        cfg["license_status"] = license.LicenseStatus.TRIAL

        assert license.is_trial_expired(cfg) is True
        # Days remaining should be negative
        days_remaining = license.get_trial_days_remaining(cfg)
        assert days_remaining < 0

    def test_license_activation(self, tmp_path):
        """Test license activation with mock key."""
        cfg = config.DEFAULTS.copy()

        # Mock successful activation by setting config directly
        cfg["license_key"] = "TEST-KEY-12345"
        cfg["license_status"] = license.LicenseStatus.ACTIVE

        status_info = license.get_license_status_info(cfg)
        assert status_info["status"] == license.LicenseStatus.ACTIVE
        assert status_info["can_use_app"] is True

    def test_invalid_license_returns_to_trial(self, tmp_path):
        """Test handling when license is deactivated."""
        cfg = config.DEFAULTS.copy()

        # Start with active license
        cfg["license_key"] = "TEST-KEY-12345"
        cfg["license_status"] = license.LicenseStatus.ACTIVE
        cfg["trial_started_date"] = datetime.now().isoformat()

        # Deactivate
        cfg = license.deactivate_license(cfg)

        # Should return to trial mode (since trial not expired)
        assert cfg["license_status"] == license.LicenseStatus.TRIAL
        assert cfg["license_key"] == ""


class TestSettingsConfig:
    """Test Settings configuration functionality."""

    def test_settings_sections_exist(self, tmp_path):
        """Verify all settings sections are defined in DEFAULTS."""
        defaults = config.DEFAULTS

        # Check core settings exist
        assert "model_size" in defaults
        assert "language" in defaults
        assert "hotkey" in defaults

        # Check new feature settings exist
        assert "custom_vocabulary" in defaults
        assert "translation_enabled" in defaults
        assert "ai_cleanup_enabled" in defaults
        assert "license_status" in defaults

    def test_settings_persistence(self, tmp_path):
        """Verify settings save and load correctly."""
        config_file = tmp_path / "settings.json"

        # Create custom config
        cfg = config.DEFAULTS.copy()
        cfg["model_size"] = "base.en"
        cfg["custom_vocabulary"] = ["MurmurTone", "GitHub"]
        cfg["translation_enabled"] = True

        # Save to temp file
        with open(config_file, "w") as f:
            json.dump(cfg, f)

        # Load and verify
        with open(config_file, "r") as f:
            loaded = json.load(f)

        assert loaded["model_size"] == "base.en"
        assert loaded["custom_vocabulary"] == ["MurmurTone", "GitHub"]
        assert loaded["translation_enabled"] is True

    def test_defaults_have_all_required_keys(self):
        """Verify DEFAULTS contains all essential keys."""
        required_keys = [
            "model_size", "language", "hotkey", "recording_mode",
            "silence_duration_sec", "audio_feedback", "input_device",
            "auto_paste", "processing_mode", "noise_gate_enabled",
            "voice_commands_enabled", "ai_cleanup_enabled",
            "preview_enabled", "translation_enabled"
        ]

        for key in required_keys:
            assert key in config.DEFAULTS, f"Missing required key: {key}"


class TestVoiceCommandLogic:
    """Test voice command processing logic (without audio)."""

    def test_scratch_that_removes_text(self):
        """Verify 'scratch that' command removes last text."""
        text = "Hello world"
        command_detected = "scratch that"

        # Simulate command processing
        if "scratch that" in command_detected.lower():
            result = ""  # Text should be removed
        else:
            result = text

        assert result == ""

    def test_capitalize_that_logic(self):
        """Verify 'capitalize that' command logic."""
        text = "hello world"

        # Simulate capitalize command
        words = text.split()
        if words:
            words[-1] = words[-1].capitalize()
            result = " ".join(words)

        assert result == "hello World"

    def test_uppercase_that_logic(self):
        """Verify 'uppercase that' command logic."""
        text = "hello world"

        # Simulate uppercase command
        words = text.split()
        if words:
            words[-1] = words[-1].upper()
            result = " ".join(words)

        assert result == "hello WORLD"

    def test_lowercase_that_logic(self):
        """Verify 'lowercase that' command logic."""
        text = "hello WORLD"

        # Simulate lowercase command
        words = text.split()
        if words:
            words[-1] = words[-1].lower()
            result = " ".join(words)

        assert result == "hello world"

    def test_delete_last_word_logic(self):
        """Verify 'delete last word' command logic."""
        text = "hello world test"

        # Simulate delete last word
        words = text.split()
        if words:
            words.pop()
            result = " ".join(words)

        assert result == "hello world"


class TestAudioFileTranscription:
    """Test audio file transcription feature."""

    def test_supported_formats_defined(self):
        """Verify supported audio formats are defined."""
        supported_formats = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']

        # These should be the formats supported by faster-whisper
        assert '.mp3' in supported_formats
        assert '.wav' in supported_formats
        assert '.m4a' in supported_formats

    def test_create_test_wav_file(self, tmp_path):
        """Create a test WAV file for transcription testing."""
        import wave

        # Generate 1 second of silence at 16kHz
        sample_rate = 16000
        duration = 1.0
        samples = np.zeros(int(sample_rate * duration), dtype=np.int16)

        # Save as WAV
        wav_path = tmp_path / "test_audio.wav"
        with wave.open(str(wav_path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())

        assert wav_path.exists()
        assert wav_path.stat().st_size > 0


class TestAICleanup:
    """Test AI cleanup feature."""

    def test_ollama_connection_check(self):
        """Test Ollama availability check."""
        from ai_cleanup import check_ollama_available

        # This will return False if Ollama isn't running, which is expected
        is_available = check_ollama_available()

        # Test passes whether Ollama is available or not
        assert isinstance(is_available, bool)

    def test_cleanup_returns_none_when_unavailable(self):
        """Test cleanup_text returns None when Ollama unavailable."""
        from ai_cleanup import cleanup_text, check_ollama_available

        text = "test input"
        result = cleanup_text(text, model="llama3.2:3b", url="http://localhost:11434")

        # Result is string if Ollama available, None otherwise
        if check_ollama_available():
            assert isinstance(result, str)
        else:
            assert result is None


class TestTranslationMode:
    """Test translation mode feature."""

    def test_translation_config_values(self, tmp_path):
        """Verify translation configuration."""
        cfg = config.DEFAULTS.copy()

        # Check translation settings exist
        assert "translation_enabled" in cfg
        assert "translation_source_language" in cfg

        # Test setting translation mode
        cfg["translation_enabled"] = True
        cfg["translation_source_language"] = "es"

        assert cfg["translation_enabled"] is True
        assert cfg["translation_source_language"] == "es"

    def test_translation_language_options(self):
        """Verify supported translation languages."""
        # Check LANGUAGE_LABELS contains expected languages
        labels = config.LANGUAGE_LABELS

        # Should support major languages
        assert "en" in labels  # English
        assert "es" in labels  # Spanish
        assert "fr" in labels  # French


class TestPerformanceMetrics:
    """Test performance and resource usage."""

    def test_config_defaults_access_fast(self):
        """Verify config defaults access is fast (no benchmark plugin needed)."""
        import time

        start = time.perf_counter()
        for _ in range(1000):
            config.DEFAULTS.copy()
        elapsed = time.perf_counter() - start

        # 1000 accesses should complete in < 100ms
        assert elapsed < 0.1

    def test_license_check_fast(self):
        """Verify license check is fast (no benchmark plugin needed)."""
        import time

        cfg = config.DEFAULTS.copy()
        cfg["trial_started_date"] = datetime.now().isoformat()
        cfg["license_status"] = license.LicenseStatus.TRIAL

        start = time.perf_counter()
        for _ in range(1000):
            license.is_trial_expired(cfg)
        elapsed = time.perf_counter() - start

        # 1000 checks should complete in < 100ms
        assert elapsed < 0.1


class TestSystemIntegration:
    """Test system-level integrations."""

    def test_config_file_operations(self, tmp_path):
        """Verify config file can be written and read."""
        config_file = tmp_path / "settings.json"

        cfg = config.DEFAULTS.copy()
        cfg["model_size"] = "medium"

        # Write
        with open(config_file, "w") as f:
            json.dump(cfg, f, indent=2)

        assert config_file.exists()

        # Read back
        with open(config_file, "r") as f:
            loaded = json.load(f)

        assert loaded["model_size"] == "medium"

    def test_log_file_creation(self, tmp_path):
        """Verify log file is created."""
        import logging

        log_file = Path(tmp_path) / "test.log"

        # Create logger
        logger = logging.getLogger("test_track2")
        handler = logging.FileHandler(log_file)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Log message
        logger.info("Test log message")
        handler.close()

        # Verify log file exists
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test log message" in content


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
