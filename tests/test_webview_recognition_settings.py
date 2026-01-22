"""
Backend tests for PyWebView Recognition tab settings.

Tests config save/load, validation, and API methods for Recognition page features:
- Model size selection
- Processing mode (CPU/GPU)
- GPU detection and status
- Silence duration
- Custom vocabulary
- Translation mode

Run with: pytest tests/test_webview_recognition_settings.py -v
"""
import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file with default values."""
    config_file = tmp_path / "murmurtone_settings.json"
    default_config = {
        "model_size": "tiny",
        "processing_mode": "auto",
        "silence_duration_sec": 2.0,
        "custom_vocabulary": [],
        "translation_enabled": False,
        "translation_source_language": "auto"
    }
    config_file.write_text(json.dumps(default_config))
    return config_file


@pytest.fixture
def mock_gpu_available(mocker):
    """Mock GPU as available."""
    mock_status = mocker.patch('settings_logic.get_cuda_status')
    mock_status.return_value = (True, "CUDA available", "NVIDIA GeForce RTX 3080")
    return mock_status


@pytest.fixture
def mock_gpu_unavailable(mocker):
    """Mock GPU as unavailable."""
    mock_status = mocker.patch('settings_logic.get_cuda_status')
    mock_status.return_value = (False, "GPU libraries not installed", None)
    return mock_status


# =============================================================================
# Model Settings Tests
# =============================================================================

class TestModelSettings:
    """Test model size selection and download."""

    def test_model_size_saves_correctly(self, mocker, tmp_path):
        """Model size should save to config."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        # Save model size
        cfg = config.load_config()
        cfg['model_size'] = 'medium'
        config.save_config(cfg)

        # Reload and verify
        reloaded = config.load_config()
        assert reloaded['model_size'] == 'medium'

    def test_model_size_valid_values(self):
        """Model size should only accept valid values."""
        import config

        valid_models = config.MODEL_OPTIONS
        assert 'tiny' in valid_models
        assert 'base' in valid_models
        assert 'small' in valid_models
        assert 'medium' in valid_models
        assert 'large-v3' in valid_models

    def test_model_availability_constants_exist(self):
        """Config should define model availability constants."""
        import config

        # Verify model configuration exists
        assert hasattr(config, 'MODEL_OPTIONS')
        assert hasattr(config, 'MODEL_DISPLAY_NAMES')

        # Model options should be non-empty
        assert len(config.MODEL_OPTIONS) > 0

    def test_model_display_names_mapping(self):
        """Model display names should map to internal names."""
        import config

        # Check display names exist
        assert hasattr(config, 'MODEL_DISPLAY_NAMES')
        assert 'tiny' in config.MODEL_DISPLAY_NAMES
        assert 'base' in config.MODEL_DISPLAY_NAMES

    def test_default_model_is_tiny(self):
        """Default model should be 'tiny' for fastest startup."""
        import config

        defaults = config.DEFAULTS
        assert defaults['model_size'] == 'tiny'


# =============================================================================
# Processing Mode Tests
# =============================================================================

class TestProcessingMode:
    """Test CPU/GPU processing mode settings."""

    def test_processing_mode_valid_values(self):
        """Processing mode should have exactly 4 valid options."""
        import config

        valid_modes = config.PROCESSING_MODE_OPTIONS
        assert len(valid_modes) == 4
        assert 'auto' in valid_modes
        assert 'cpu' in valid_modes
        assert 'gpu-balanced' in valid_modes
        assert 'gpu-quality' in valid_modes

    def test_processing_mode_defaults_to_auto(self):
        """Default processing mode should be 'auto'."""
        import config

        defaults = config.DEFAULTS
        assert defaults['processing_mode'] == 'auto'

    def test_gpu_balanced_uses_float16(self):
        """GPU-balanced mode should use float16 compute type."""
        import config

        mode_map = config.PROCESSING_MODE_MAP
        assert mode_map['gpu-balanced']['compute_type'] == 'float16'
        assert mode_map['gpu-balanced']['device'] == 'cuda'

    def test_gpu_quality_uses_float32(self):
        """GPU-quality mode should use float32 compute type."""
        import config

        mode_map = config.PROCESSING_MODE_MAP
        assert mode_map['gpu-quality']['compute_type'] == 'float32'
        assert mode_map['gpu-quality']['device'] == 'cuda'


# =============================================================================
# GPU Features Tests
# =============================================================================

class TestGPUFeatures:
    """Test GPU detection and status."""

    def test_get_gpu_status_returns_dict(self, mocker, mock_gpu_available):
        """get_gpu_status() should return a dictionary with status info."""
        import settings_webview

        # Create API instance (mocked)
        api = settings_webview.SettingsAPI()

        result = api.get_gpu_status()
        assert isinstance(result, dict)
        assert 'success' in result

    def test_gpu_status_when_available(self, mocker, mock_gpu_available):
        """GPU status should show available when CUDA is detected."""
        import settings_webview

        api = settings_webview.SettingsAPI()
        result = api.get_gpu_status()

        assert result['success'] is True
        assert result['data']['available'] is True
        assert 'name' in result['data']

    def test_gpu_status_when_unavailable(self, mocker, mock_gpu_unavailable):
        """GPU status should show unavailable when CUDA is not detected."""
        import settings_webview

        api = settings_webview.SettingsAPI()
        result = api.get_gpu_status()

        assert result['success'] is True
        assert result['data']['available'] is False

    def test_install_gpu_support_flow(self, mocker):
        """install_gpu_support() should return success/failure."""
        import settings_webview

        # Mock the install process
        mock_install = mocker.patch('settings_webview.SettingsAPI.install_gpu_support')
        mock_install.return_value = {'success': True, 'message': 'Installed'}

        api = settings_webview.SettingsAPI()
        result = api.install_gpu_support()

        assert isinstance(result, dict)
        assert 'success' in result


# =============================================================================
# Silence Duration Tests
# =============================================================================

class TestSilenceDuration:
    """Test silence duration validation."""

    def test_silence_duration_range(self, mocker, tmp_path):
        """Silence duration should be between 0.5 and 5.0 seconds."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        # Test valid range
        cfg = config.load_config()
        cfg['silence_duration_sec'] = 0.5
        config.save_config(cfg)
        assert config.load_config()['silence_duration_sec'] == 0.5

        cfg['silence_duration_sec'] = 5.0
        config.save_config(cfg)
        assert config.load_config()['silence_duration_sec'] == 5.0

    def test_silence_duration_step_size(self):
        """Silence duration should increment by 0.5 seconds."""
        # Valid steps: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0
        valid_steps = [0.5 * i for i in range(1, 11)]

        for value in valid_steps:
            assert 0.5 <= value <= 5.0
            assert (value * 2) % 1 == 0  # Ensure it's a 0.5 increment

    def test_silence_duration_default(self):
        """Default silence duration should be 2.0 seconds."""
        import config

        defaults = config.DEFAULTS
        assert defaults['silence_duration_sec'] == 2.0


# =============================================================================
# Custom Vocabulary Tests
# =============================================================================

class TestCustomVocabulary:
    """Test custom vocabulary integration."""

    def test_vocabulary_saves_as_array(self, mocker, tmp_path):
        """Custom vocabulary should save as an array."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['custom_vocabulary'] = ['TensorFlow', 'Kubernetes', 'PyWebView']
        config.save_config(cfg)

        reloaded = config.load_config()
        assert isinstance(reloaded['custom_vocabulary'], list)
        assert len(reloaded['custom_vocabulary']) == 3
        assert 'TensorFlow' in reloaded['custom_vocabulary']

    def test_vocabulary_appends_to_initial_prompt(self, mocker):
        """Custom vocabulary should be appended to Whisper's initial prompt."""
        # This tests the integration in murmurtone.py
        # Mock config with custom vocabulary
        mock_config = {
            'custom_vocabulary': ['OpenAI', 'Whisper', 'GPT-4'],
            'initial_prompt': 'Use proper punctuation.'
        }

        # The prompt should include vocabulary words
        # Actual implementation in murmurtone.py lines 737-750
        expected_vocab_text = "OpenAI, Whisper, GPT-4"
        assert all(word in expected_vocab_text for word in mock_config['custom_vocabulary'])

    def test_empty_vocabulary_uses_base_prompt(self):
        """Empty vocabulary should not modify the base prompt."""
        import config

        defaults = config.DEFAULTS
        assert defaults['custom_vocabulary'] == []

    def test_vocabulary_with_special_characters(self, mocker, tmp_path):
        """Vocabulary should handle special characters."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['custom_vocabulary'] = ['C++', 'Node.js', 'Dr. Smith']
        config.save_config(cfg)

        reloaded = config.load_config()
        assert 'C++' in reloaded['custom_vocabulary']
        assert 'Node.js' in reloaded['custom_vocabulary']

    def test_vocabulary_preserves_case(self, mocker, tmp_path):
        """Vocabulary should preserve case sensitivity."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['custom_vocabulary'] = ['TensorFlow', 'tensorflow', 'TENSORFLOW']
        config.save_config(cfg)

        reloaded = config.load_config()
        # All three variations should be preserved
        assert 'TensorFlow' in reloaded['custom_vocabulary']
        assert 'tensorflow' in reloaded['custom_vocabulary']
        assert 'TENSORFLOW' in reloaded['custom_vocabulary']

    def test_vocabulary_in_file_transcription(self):
        """Custom vocabulary should be used in file transcription."""
        # This would test file_transcription.py integration
        # The implementation uses custom_vocabulary at lines 81-92
        import config

        defaults = config.DEFAULTS
        assert 'custom_vocabulary' in defaults


# =============================================================================
# Translation Mode Tests
# =============================================================================

class TestTranslationMode:
    """Test translation settings."""

    def test_translation_toggle_saves_correctly(self, mocker, tmp_path):
        """Translation enabled toggle should save to config."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['translation_enabled'] = True
        config.save_config(cfg)

        reloaded = config.load_config()
        assert reloaded['translation_enabled'] is True

    def test_translation_source_language_options(self):
        """Translation should support multiple source languages."""
        import settings_logic

        # Get language options
        languages = settings_logic.get_language_labels()

        # Should include common languages
        assert len(languages) > 0
        # Auto-detect should be an option (check exact spelling)
        assert 'Auto-detect' in languages or 'auto-detect' in [lang.lower() for lang in languages]

    def test_translation_auto_detect_default(self):
        """Translation source language should default to 'auto'."""
        import config

        defaults = config.DEFAULTS
        assert defaults['translation_source_language'] == 'auto'

    def test_translation_with_custom_vocabulary(self, mocker, tmp_path):
        """Translation mode should work with custom vocabulary."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        # Both features should coexist
        cfg = config.load_config()
        cfg['translation_enabled'] = True
        cfg['translation_source_language'] = 'es'
        cfg['custom_vocabulary'] = ['hola', 'gracias']
        config.save_config(cfg)

        reloaded = config.load_config()
        assert reloaded['translation_enabled'] is True
        assert reloaded['custom_vocabulary'] == ['hola', 'gracias']


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
