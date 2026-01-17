"""
Tests for model download and availability checking functionality.
"""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestModelConstants:
    """Test model-related constants in config."""

    def test_bundled_models_defined(self):
        """BUNDLED_MODELS constant should be defined."""
        import config
        assert hasattr(config, 'BUNDLED_MODELS')
        assert isinstance(config.BUNDLED_MODELS, list)
        assert len(config.BUNDLED_MODELS) > 0

    def test_downloadable_models_defined(self):
        """DOWNLOADABLE_MODELS constant should be defined."""
        import config
        assert hasattr(config, 'DOWNLOADABLE_MODELS')
        assert isinstance(config.DOWNLOADABLE_MODELS, list)

    def test_model_sizes_defined(self):
        """MODEL_SIZES_MB constant should be defined for all models."""
        import config
        assert hasattr(config, 'MODEL_SIZES_MB')
        assert isinstance(config.MODEL_SIZES_MB, dict)

        # All models should have size defined
        all_models = config.BUNDLED_MODELS + config.DOWNLOADABLE_MODELS
        for model in all_models:
            assert model in config.MODEL_SIZES_MB, f"Size not defined for {model}"
            assert config.MODEL_SIZES_MB[model] > 0

    def test_model_download_urls_defined(self):
        """MODEL_DOWNLOAD_URLS should be defined for downloadable models."""
        import config
        assert hasattr(config, 'MODEL_DOWNLOAD_URLS')
        assert isinstance(config.MODEL_DOWNLOAD_URLS, dict)

        # All downloadable models should have URLs
        for model in config.DOWNLOADABLE_MODELS:
            assert model in config.MODEL_DOWNLOAD_URLS, f"URL not defined for {model}"
            assert config.MODEL_DOWNLOAD_URLS[model].startswith('https://')

    def test_bundled_and_downloadable_are_disjoint(self):
        """Bundled and downloadable models should not overlap."""
        import config
        bundled_set = set(config.BUNDLED_MODELS)
        downloadable_set = set(config.DOWNLOADABLE_MODELS)
        overlap = bundled_set & downloadable_set
        assert len(overlap) == 0, f"Models in both lists: {overlap}"

    def test_all_models_in_model_options(self):
        """All bundled and downloadable models should be in MODEL_OPTIONS."""
        import config
        all_models = set(config.BUNDLED_MODELS + config.DOWNLOADABLE_MODELS)
        options_set = set(config.MODEL_OPTIONS)
        missing = all_models - options_set
        assert len(missing) == 0, f"Models not in MODEL_OPTIONS: {missing}"


class TestCheckModelAvailable:
    """Test check_model_available function."""

    def test_check_bundled_model_exists(self, tmp_path):
        """Should return True for bundled model that exists."""
        from dependency_check import check_model_available, get_app_install_dir

        # Create a fake bundled model
        models_dir = tmp_path / "models" / "tiny.en"
        models_dir.mkdir(parents=True)
        (models_dir / "model.bin").write_text("fake model")

        with patch('dependency_check.get_app_install_dir', return_value=str(tmp_path)):
            is_available, path = check_model_available("tiny.en")
            assert is_available is True
            assert path is not None
            assert "tiny.en" in path

    def test_check_model_missing(self, tmp_path):
        """Should return False for model that doesn't exist."""
        from dependency_check import check_model_available

        with patch('dependency_check.get_app_install_dir', return_value=str(tmp_path)):
            # Also mock HuggingFace cache to not exist
            with patch('pathlib.Path.home', return_value=tmp_path):
                is_available, path = check_model_available("nonexistent.model")
                assert is_available is False
                assert path is None

    def test_check_model_dir_exists_but_no_model_bin(self, tmp_path):
        """Should return False if model dir exists but model.bin is missing."""
        from dependency_check import check_model_available

        # Create model directory without model.bin
        models_dir = tmp_path / "models" / "tiny.en"
        models_dir.mkdir(parents=True)
        (models_dir / "config.json").write_text("{}")  # Some other file

        with patch('dependency_check.get_app_install_dir', return_value=str(tmp_path)):
            with patch('pathlib.Path.home', return_value=tmp_path):
                is_available, path = check_model_available("tiny.en")
                assert is_available is False


class TestGetSelectedModel:
    """Test get_selected_model function."""

    def test_get_selected_model_default(self, tmp_path):
        """Should return default model when config is empty."""
        from dependency_check import get_selected_model

        config_file = tmp_path / "config.json"
        config_file.write_text("{}")

        with patch('config.get_config_path', return_value=str(config_file)):
            model = get_selected_model()
            assert model == "tiny.en"

    def test_get_selected_model_from_config(self, tmp_path):
        """Should return model from config."""
        from dependency_check import get_selected_model
        import json

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"model_size": "small.en"}))

        with patch('config.get_config_path', return_value=str(config_file)):
            model = get_selected_model()
            assert model == "small.en"


class TestGetModelDownloadUrl:
    """Test model download URL generation."""

    def test_download_url_format(self):
        """Download URLs should use expected format."""
        import config

        for model, url in config.MODEL_DOWNLOAD_URLS.items():
            assert "github.com" in url
            assert "releases" in url
            assert model in url or model.replace(".", "") in url


class TestModelSizeConstants:
    """Test model size constants match expected values."""

    def test_tiny_model_size(self):
        """tiny.en should be approximately 75 MB."""
        import config
        size = config.MODEL_SIZES_MB.get("tiny.en", 0)
        assert 50 <= size <= 100, f"tiny.en size {size}MB outside expected range"

    def test_base_model_size(self):
        """base.en should be approximately 145 MB."""
        import config
        size = config.MODEL_SIZES_MB.get("base.en", 0)
        assert 100 <= size <= 200, f"base.en size {size}MB outside expected range"

    def test_small_model_size(self):
        """small.en should be approximately 484 MB."""
        import config
        size = config.MODEL_SIZES_MB.get("small.en", 0)
        assert 400 <= size <= 600, f"small.en size {size}MB outside expected range"

    def test_medium_model_size(self):
        """medium.en should be approximately 1500 MB."""
        import config
        size = config.MODEL_SIZES_MB.get("medium.en", 0)
        assert 1200 <= size <= 1800, f"medium.en size {size}MB outside expected range"


class TestSetFallbackModel:
    """Test set_fallback_model function."""

    def test_set_fallback_model(self, tmp_path):
        """Should update config with fallback model."""
        from dependency_check import set_fallback_model
        import json

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"model_size": "small.en"}))

        with patch('config.get_config_path', return_value=str(config_file)):
            result = set_fallback_model("base.en")
            assert result is True

            # Verify config was updated
            updated_config = json.loads(config_file.read_text())
            assert updated_config["model_size"] == "base.en"
