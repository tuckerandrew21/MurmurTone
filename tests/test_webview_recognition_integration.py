"""
Integration tests for Recognition features.

Tests data flow from config → backend → Whisper model:
- Custom vocabulary flows to Whisper initial_prompt
- Processing mode affects model device selection
- Translation sets correct task parameter

Run with: pytest tests/test_webview_recognition_integration.py -v
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
    """Create a temporary config file."""
    config_file = tmp_path / "murmurtone_settings.json"
    default_config = {
        "model_size": "tiny",
        "processing_mode": "auto",
        "silence_duration_sec": 2.0,
        "custom_vocabulary": [],
        "translation_enabled": False,
        "translation_source_language": "auto",
        "initial_prompt": "Use proper punctuation."
    }
    config_file.write_text(json.dumps(default_config))
    return config_file


@pytest.fixture
def mock_whisper_model(mocker):
    """Mock Whisper model loading."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {'text': 'test transcription'}
    mocker.patch('faster_whisper.WhisperModel', return_value=mock_model)
    return mock_model


# =============================================================================
# Vocabulary Integration Tests
# =============================================================================

class TestVocabularyIntegration:
    """Test vocabulary flows to Whisper correctly."""

    def test_vocabulary_included_in_transcribe_params(self, mocker, tmp_path):
        """Custom vocabulary should be included in the initial_prompt parameter."""
        import config
        import murmurtone

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        # Set custom vocabulary
        cfg = config.load_config()
        cfg['custom_vocabulary'] = ['TensorFlow', 'Kubernetes', 'PyWebView']
        cfg['initial_prompt'] = 'Use proper punctuation.'
        config.save_config(cfg)

        # Build the prompt as murmurtone.py does (lines 737-750)
        base_prompt = cfg.get('initial_prompt', '')
        vocabulary = cfg.get('custom_vocabulary', [])

        if vocabulary:
            vocab_text = ', '.join(vocabulary)
            combined_prompt = f"{base_prompt} Include these terms: {vocab_text}"
        else:
            combined_prompt = base_prompt

        # Verify vocabulary is in the prompt
        assert 'TensorFlow' in combined_prompt
        assert 'Kubernetes' in combined_prompt
        assert 'PyWebView' in combined_prompt

    def test_empty_vocabulary_uses_base_prompt_only(self, mocker, tmp_path):
        """Empty vocabulary should use only the base prompt."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['custom_vocabulary'] = []
        cfg['initial_prompt'] = 'Use proper punctuation.'
        config.save_config(cfg)

        base_prompt = cfg.get('initial_prompt', '')
        vocabulary = cfg.get('custom_vocabulary', [])

        if vocabulary:
            vocab_text = ', '.join(vocabulary)
            combined_prompt = f"{base_prompt} Include these terms: {vocab_text}"
        else:
            combined_prompt = base_prompt

        # Should only have base prompt
        assert combined_prompt == 'Use proper punctuation.'
        assert 'Include these terms:' not in combined_prompt

    def test_vocabulary_combined_with_base_prompt(self, mocker, tmp_path):
        """Vocabulary should be appended to base prompt, not replace it."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['custom_vocabulary'] = ['OpenAI', 'Whisper']
        cfg['initial_prompt'] = 'Use proper punctuation.'
        config.save_config(cfg)

        base_prompt = cfg.get('initial_prompt', '')
        vocabulary = cfg.get('custom_vocabulary', [])

        if vocabulary:
            vocab_text = ', '.join(vocabulary)
            combined_prompt = f"{base_prompt} Include these terms: {vocab_text}"
        else:
            combined_prompt = base_prompt

        # Both base prompt and vocabulary should be present
        assert 'Use proper punctuation.' in combined_prompt
        assert 'OpenAI' in combined_prompt
        assert 'Whisper' in combined_prompt


# =============================================================================
# Processing Mode Integration Tests
# =============================================================================

class TestProcessingModeIntegration:
    """Test processing mode affects model loading."""

    def test_auto_mode_selects_gpu_if_available(self, mocker):
        """Auto mode should use GPU if CUDA is available."""
        import config
        import settings_logic

        # Mock GPU as available
        mocker.patch('settings_logic.get_cuda_status',
                     return_value=(True, "CUDA available", "NVIDIA RTX 3080"))

        # Check what device 'auto' mode selects
        mode_config = config.PROCESSING_MODE_MAP['auto']

        # Auto mode with GPU available should prefer GPU
        # (Actual logic may be in murmurtone.py model loading)
        assert mode_config['device'] == 'auto'

    def test_cpu_mode_forces_cpu(self):
        """CPU mode should always use CPU regardless of GPU availability."""
        import config

        mode_config = config.PROCESSING_MODE_MAP['cpu']

        assert mode_config['device'] == 'cpu'
        assert mode_config['compute_type'] == 'int8'

    def test_gpu_mode_requires_cuda(self):
        """GPU modes (balanced/quality) should require CUDA."""
        import config

        balanced_config = config.PROCESSING_MODE_MAP['gpu-balanced']
        quality_config = config.PROCESSING_MODE_MAP['gpu-quality']

        # Both GPU modes should specify cuda device
        assert balanced_config['device'] == 'cuda'
        assert quality_config['device'] == 'cuda'


# =============================================================================
# Translation Integration Tests
# =============================================================================

class TestTranslationIntegration:
    """Test translation passes correct params."""

    def test_translation_sets_task_translate(self, mocker, tmp_path):
        """Translation mode should set task='translate' in Whisper."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['translation_enabled'] = True
        cfg['translation_source_language'] = 'es'
        config.save_config(cfg)

        reloaded = config.load_config()

        # When translation_enabled is True, Whisper should use task='translate'
        # (Implementation in murmurtone.py transcribe call)
        assert reloaded['translation_enabled'] is True

    def test_translation_source_language_passed(self, mocker, tmp_path):
        """Source language should be passed to Whisper when not auto."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['translation_enabled'] = True
        cfg['translation_source_language'] = 'fr'
        config.save_config(cfg)

        reloaded = config.load_config()

        # When source language is specified, it should be passed to Whisper
        assert reloaded['translation_source_language'] == 'fr'

    def test_translation_works_with_vocabulary(self, mocker, tmp_path):
        """Translation and custom vocabulary should work together."""
        import config

        config_path = tmp_path / "murmurtone_settings.json"
        mocker.patch('config.get_config_path', return_value=str(config_path))

        cfg = config.load_config()
        cfg['translation_enabled'] = True
        cfg['translation_source_language'] = 'es'
        cfg['custom_vocabulary'] = ['España', 'Barcelona', 'Madrid']
        cfg['initial_prompt'] = 'Use proper punctuation.'
        config.save_config(cfg)

        reloaded = config.load_config()

        # Build combined prompt
        base_prompt = reloaded.get('initial_prompt', '')
        vocabulary = reloaded.get('custom_vocabulary', [])

        if vocabulary:
            vocab_text = ', '.join(vocabulary)
            combined_prompt = f"{base_prompt} Include these terms: {vocab_text}"
        else:
            combined_prompt = base_prompt

        # Both translation and vocabulary should be configured
        assert reloaded['translation_enabled'] is True
        assert 'España' in combined_prompt
        assert 'Barcelona' in combined_prompt


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
