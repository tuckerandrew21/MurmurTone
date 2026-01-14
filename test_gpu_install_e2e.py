"""End-to-end test for GPU install - runs the actual pip installation."""

import sys
import os
import subprocess

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import settings_logic


def run_test():
    """Run the full GPU installation test."""
    print("=" * 60)
    print("GPU Install E2E Test")
    print("=" * 60)

    # Step 1: Check initial GPU status
    print("\n[1] Checking initial GPU status...")
    is_available, status_msg, gpu_name = settings_logic.get_cuda_status()
    print(f"    Available: {is_available}")
    print(f"    Status: {status_msg}")
    print(f"    GPU Name: {gpu_name}")

    if is_available:
        print("\n[SKIP] GPU libraries already installed.")
        print("       Button would be HIDDEN (correct behavior)")
        return True

    if status_msg != "GPU libraries not installed":
        print(f"\n[SKIP] GPU unavailable for different reason: {status_msg}")
        print("       Button would be HIDDEN (correct behavior)")
        return True

    print("\n    Button would be VISIBLE (correct behavior)")

    # Step 2: Find requirements file
    print("\n[2] Locating requirements-gpu.txt...")
    req_file = os.path.join(os.path.dirname(__file__), "requirements-gpu.txt")
    if not os.path.exists(req_file):
        print(f"    [ERROR] File not found: {req_file}")
        return False
    print(f"    Found: {req_file}")

    # Step 3: Run pip install (same command the button uses)
    print("\n[3] Running pip install (this downloads ~2-3 GB)...")
    print("    Command: pip install -r requirements-gpu.txt")
    print("    Please wait...\n")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req_file],
        capture_output=False,  # Show output in real-time
    )

    if result.returncode != 0:
        print(f"\n[ERROR] pip install failed with code {result.returncode}")
        return False

    print("\n    pip install completed successfully!")

    # Step 4: Verify GPU status changed
    print("\n[4] Verifying GPU status after installation...")

    # Force reimport to pick up newly installed libraries
    import importlib
    importlib.reload(settings_logic)

    is_available, status_msg, gpu_name = settings_logic.get_cuda_status()
    print(f"    Available: {is_available}")
    print(f"    Status: {status_msg}")
    print(f"    GPU Name: {gpu_name}")

    if status_msg == "GPU libraries not installed":
        print("\n[FAIL] GPU libraries still show as not installed!")
        print("       (This might require a Python restart to detect)")
        return False

    # Step 5: Verify button would be hidden
    print("\n[5] Verifying button visibility logic...")
    should_show = not is_available and status_msg == "GPU libraries not installed"
    print(f"    Button should show: {should_show}")

    if should_show:
        print("\n[WARN] Button would still show - libraries may need restart to detect")
    else:
        print("    Button would be HIDDEN (correct behavior)")

    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
