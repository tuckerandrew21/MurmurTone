"""
Package Whisper models for MurmurTone GitHub release.

This script downloads models from HuggingFace (if needed) and packages
them into ZIP files for GitHub release.

Usage:
    python package_models.py                    # Package all downloadable models
    python package_models.py small.en           # Package specific model
    python package_models.py small.en medium.en # Package multiple models

Output:
    dist/faster-whisper-small.en.zip    - Ready for GitHub release
    dist/faster-whisper-medium.en.zip   - Ready for GitHub release
"""
import os
import sys
import shutil
import zipfile
from pathlib import Path

# Import from prepare_model.py
from prepare_model import find_model_in_cache, download_model_if_needed

# Default models to package (the downloadable ones, not bundled)
try:
    from config import DOWNLOADABLE_MODELS, MODEL_SIZES_MB
except ImportError:
    DOWNLOADABLE_MODELS = ["small.en", "medium.en"]
    MODEL_SIZES_MB = {"small.en": 484, "medium.en": 1500}

OUTPUT_DIR = "dist"


def package_model(model_name: str) -> bool:
    """
    Package a single model into a ZIP file.

    Args:
        model_name: Name of the model (e.g., "small.en")

    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'=' * 50}")
    print(f"Packaging {model_name}")
    print("=" * 50)

    # Get model from cache (download if needed)
    try:
        model_path = download_model_if_needed(model_name)
    except Exception as e:
        print(f"ERROR: Failed to get model: {e}")
        return False

    if not model_path or not Path(model_path).exists():
        print(f"ERROR: Model path not found: {model_path}")
        return False

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # ZIP file name
    zip_name = f"faster-whisper-{model_name}.zip"
    zip_path = Path(OUTPUT_DIR) / zip_name

    # Remove existing ZIP if present
    if zip_path.exists():
        print(f"Removing existing {zip_path}...")
        zip_path.unlink()

    # Create ZIP with model files
    print(f"Creating {zip_path}...")
    model_files = list(Path(model_path).iterdir())
    total_size = 0

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in model_files:
            if file.is_file():
                # Store with model_name prefix so extraction creates the right folder
                arcname = f"{model_name}/{file.name}"
                zf.write(file, arcname)
                size = file.stat().st_size
                total_size += size
                print(f"  + {file.name} ({size / 1024 / 1024:.1f} MB)")

    zip_size = zip_path.stat().st_size
    compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0

    print(f"\n✓ Created: {zip_path}")
    print(f"  Original size: {total_size / 1024 / 1024:.1f} MB")
    print(f"  ZIP size: {zip_size / 1024 / 1024:.1f} MB")
    print(f"  Compression: {compression_ratio:.1f}%")

    return True


def main():
    """Main entry point."""
    print("MurmurTone Model Packager")
    print("=" * 50)

    # Determine which models to package
    if len(sys.argv) > 1:
        models_to_package = sys.argv[1:]
    else:
        models_to_package = DOWNLOADABLE_MODELS

    print(f"Models to package: {', '.join(models_to_package)}")

    # Estimate total download size
    total_estimated = sum(MODEL_SIZES_MB.get(m, 500) for m in models_to_package)
    print(f"Estimated total download: ~{total_estimated} MB")

    # Package each model
    success_count = 0
    for model_name in models_to_package:
        if package_model(model_name):
            success_count += 1

    # Summary
    print("\n" + "=" * 50)
    if success_count == len(models_to_package):
        print("SUCCESS!")
        print(f"\nCreated {success_count} ZIP file(s) in {OUTPUT_DIR}/")
        print("\nUpload to GitHub release:")
        print("  https://github.com/tuckerandrew21/MurmurTone/releases/new")
        print("  Tag: models-v1.0.0")
        print("\nFiles to upload:")
        for model_name in models_to_package:
            zip_name = f"faster-whisper-{model_name}.zip"
            zip_path = Path(OUTPUT_DIR) / zip_name
            if zip_path.exists():
                size_mb = zip_path.stat().st_size / 1024 / 1024
                print(f"  - {zip_name} ({size_mb:.1f} MB)")
        return 0
    else:
        print(f"PARTIAL SUCCESS: {success_count}/{len(models_to_package)} models packaged")
        return 1


if __name__ == "__main__":
    sys.exit(main())
