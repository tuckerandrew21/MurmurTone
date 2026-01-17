"""
Package GPU libraries for MurmurTone release.

This script collects CUDA DLLs from pip-installed nvidia packages
and packages them into a zip file for GitHub release.

Usage:
    python package_gpu_libs.py

Output:
    gpu_libs/                     - Folder with all DLLs
    murmurtone-gpu-libs.zip       - Ready for GitHub release
"""
import os
import shutil
import zipfile
import sys
from pathlib import Path

# DLL sources - paths relative to site-packages
DLL_SOURCES = {
    "nvidia.cublas.bin": [
        "cublas64_12.dll",
        "cublasLt64_12.dll",
    ],
    "nvidia.cudnn.bin": [
        "cudnn64_9.dll",
        "cudnn_ops64_9.dll",
        "cudnn_cnn64_9.dll",
        "cudnn_adv64_9.dll",
        "cudnn_engines_precompiled64_9.dll",
        "cudnn_engines_runtime_compiled64_9.dll",
        "cudnn_graph64_9.dll",
        "cudnn_heuristic64_9.dll",
    ],
}

OUTPUT_DIR = "gpu_libs"
ZIP_NAME = "murmurtone-gpu-libs.zip"


def find_site_packages():
    """Find the site-packages directory."""
    for path in sys.path:
        if "site-packages" in path and os.path.isdir(path):
            return path
    raise RuntimeError("Could not find site-packages directory")


def get_dll_path(site_packages, module_path, dll_name):
    """Get full path to a DLL."""
    # Convert module path like "nvidia.cublas.bin" to path
    module_dir = module_path.replace(".", os.sep)
    return os.path.join(site_packages, module_dir, dll_name)


def main():
    print("MurmurTone GPU Library Packager")
    print("=" * 40)

    # Find site-packages
    try:
        site_packages = find_site_packages()
        print(f"Site-packages: {site_packages}")
    except RuntimeError as e:
        print(f"ERROR: {e}")
        return 1

    # Create output directory
    if os.path.exists(OUTPUT_DIR):
        print(f"Removing existing {OUTPUT_DIR}/...")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Copy DLLs
    copied = []
    missing = []
    total_size = 0

    print(f"\nCopying DLLs to {OUTPUT_DIR}/...")
    for module_path, dlls in DLL_SOURCES.items():
        for dll in dlls:
            src = get_dll_path(site_packages, module_path, dll)
            dst = os.path.join(OUTPUT_DIR, dll)

            if os.path.exists(src):
                shutil.copy2(src, dst)
                size = os.path.getsize(src)
                total_size += size
                copied.append(dll)
                print(f"  + {dll} ({size / 1024 / 1024:.1f} MB)")
            else:
                missing.append(dll)
                print(f"  ! {dll} - NOT FOUND")

    print(f"\nCopied: {len(copied)} files ({total_size / 1024 / 1024:.1f} MB)")

    if missing:
        print(f"Missing: {len(missing)} files")
        print("  " + ", ".join(missing))
        print("\nWARNING: Some DLLs are missing. Install nvidia-cublas-cu12 and nvidia-cudnn-cu12:")
        print("  pip install nvidia-cublas-cu12 nvidia-cudnn-cu12")
        return 1

    # Create zip
    print(f"\nCreating {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dll in copied:
            dll_path = os.path.join(OUTPUT_DIR, dll)
            zf.write(dll_path, dll)
            print(f"  + {dll}")

    zip_size = os.path.getsize(ZIP_NAME)
    print(f"\nCreated: {ZIP_NAME} ({zip_size / 1024 / 1024:.1f} MB)")

    # Summary
    print("\n" + "=" * 40)
    print("SUCCESS!")
    print(f"\nFiles ready for release:")
    print(f"  1. {OUTPUT_DIR}/ - For installer bundling")
    print(f"  2. {ZIP_NAME} - For GitHub release")
    print(f"\nUpload {ZIP_NAME} to:")
    print(f"  https://github.com/tuckerandrew21/MurmurTone/releases/new")
    print(f"  Tag: gpu-libs-v1.0.0")

    return 0


if __name__ == "__main__":
    sys.exit(main())
