"""
Prepare tiny.en model for bundling with PyInstaller.

This script downloads the tiny.en model (if needed) and copies it to
the models/ directory so PyInstaller can bundle it into the EXE.

Usage:
    python prepare_model.py
"""
import os
import shutil
from pathlib import Path


def get_huggingface_cache_dir():
    """Get the HuggingFace cache directory path."""
    # Default HuggingFace cache location
    home = Path.home()
    cache_dir = home / ".cache" / "huggingface" / "hub"
    return cache_dir


def find_model_in_cache(model_name="tiny.en"):
    """
    Find the downloaded Whisper model in HuggingFace cache.

    Returns path to model directory if found, None otherwise.
    """
    cache_dir = get_huggingface_cache_dir()

    if not cache_dir.exists():
        return None

    # faster-whisper downloads models to cache with pattern:
    # models--Systran--faster-whisper-tiny.en/snapshots/<hash>/
    pattern = f"models--Systran--faster-whisper-{model_name}"

    for item in cache_dir.iterdir():
        if item.is_dir() and item.name.startswith(pattern):
            # Find the snapshots directory
            snapshots_dir = item / "snapshots"
            if snapshots_dir.exists():
                # Get the first (and usually only) snapshot
                snapshots = list(snapshots_dir.iterdir())
                if snapshots:
                    return snapshots[0]

    return None


def download_model_if_needed(model_name="tiny.en"):
    """
    Download the model using faster-whisper if not already cached.

    Returns path to model directory.
    """
    print(f"Checking if {model_name} model is cached...")

    model_path = find_model_in_cache(model_name)

    if model_path:
        print(f"✓ Model found in cache: {model_path}")
        return model_path

    print(f"Model not found in cache. Downloading {model_name}...")
    print("This may take a few minutes (~150MB download)...")

    # Import here so script doesn't fail if faster-whisper not installed
    from faster_whisper import WhisperModel

    # Download model (will cache automatically)
    print("Initializing WhisperModel (this triggers download)...")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    print("✓ Model downloaded successfully!")

    # Now find it in cache
    model_path = find_model_in_cache(model_name)

    if not model_path:
        raise RuntimeError("Model was downloaded but couldn't be found in cache")

    return model_path


def prepare_bundled_model(model_name="tiny.en", target_dir="models"):
    """
    Copy model from HuggingFace cache to models/ directory for bundling.

    Args:
        model_name: Name of the model (e.g., "tiny.en")
        target_dir: Directory to copy model to (default: "models")
    """
    # Get model from cache (download if needed)
    source_path = download_model_if_needed(model_name)

    # Create target directory structure
    target_path = Path(target_dir) / model_name
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing bundled model if present
    if target_path.exists():
        print(f"Removing existing bundled model at {target_path}...")
        shutil.rmtree(target_path)

    # Copy model files
    print(f"Copying model files to {target_path}...")
    shutil.copytree(source_path, target_path)

    # Check copied files
    model_files = list(target_path.iterdir())
    total_size = sum(f.stat().st_size for f in model_files if f.is_file())
    size_mb = total_size / (1024 * 1024)

    print(f"✓ Model prepared for bundling!")
    print(f"  Location: {target_path}")
    print(f"  Files: {len(model_files)}")
    print(f"  Size: {size_mb:.1f} MB")
    print()
    print("You can now build the installer with: python build.bat")


def main():
    """Main entry point."""
    print("=" * 60)
    print("MurmurTone - Model Bundling Preparation")
    print("=" * 60)
    print()

    try:
        prepare_bundled_model("tiny.en")
        print()
        print("=" * 60)
        print("SUCCESS: Model ready for bundling")
        print("=" * 60)
        return 0

    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
