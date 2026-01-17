"""
Live integration tests for Ollama AI cleanup.

Tests the actual Ollama service with real requests.
Requires Ollama to be running with llama3.2:3b model installed.
"""

import sys
import time
from typing import Optional

sys.path.insert(0, '.')
from ai_cleanup import (
    check_ollama_available,
    get_available_models,
    cleanup_text,
    test_ollama_connection
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_result(label: str, original: str, result: Optional[str], elapsed: float) -> bool:
    """Print test result and return success status."""
    success = result is not None and len(result) > 0
    status = "[PASS]" if success else "[FAIL]"

    print(f"{status} - {label}")
    print(f"  Original:  {original}")
    print(f"  Result:    {result if result else 'None'}")
    print(f"  Time:      {elapsed:.2f}s")
    print()

    return success


def test_grammar_mode() -> tuple[int, int]:
    """Test grammar correction mode."""
    print_section("Grammar Mode Tests")

    tests = [
        "hey can u help me with this thing i dunno how to do it",
        "i aint got no time for that right now",
        "your really gonna love this its amazing",
        "theres alot of things we need to fix here"
    ]

    passed = 0
    failed = 0

    for test_text in tests:
        start = time.time()
        result = cleanup_text(test_text, mode="grammar", model="llama3.2:3b")
        elapsed = time.time() - start

        if print_result("Grammar Fix", test_text, result, elapsed):
            passed += 1
        else:
            failed += 1

    return passed, failed


def test_formality_mode() -> tuple[int, int]:
    """Test formality adjustment mode."""
    print_section("Formality Mode Tests")

    tests = [
        ("hey boss can we chat about that project thing?", "professional"),
        ("yo dude whats up with the deadline?", "formal"),
        ("i was thinking maybe we could try this approach", "professional"),
    ]

    passed = 0
    failed = 0

    for test_text, formality_level in tests:
        start = time.time()
        result = cleanup_text(
            test_text,
            mode="formality",
            formality_level=formality_level,
            model="llama3.2:3b"
        )
        elapsed = time.time() - start

        if print_result(f"Formality ({formality_level})", test_text, result, elapsed):
            passed += 1
        else:
            failed += 1

    return passed, failed


def test_both_mode() -> tuple[int, int]:
    """Test combined grammar + formality mode."""
    print_section("Combined Mode Tests (Grammar + Formality)")

    tests = [
        ("hey can u help me real quick with this thing", "professional"),
        ("yo i aint sure bout this approach", "formal"),
    ]

    passed = 0
    failed = 0

    for test_text, formality_level in tests:
        start = time.time()
        result = cleanup_text(
            test_text,
            mode="both",
            formality_level=formality_level,
            model="llama3.2:3b"
        )
        elapsed = time.time() - start

        if print_result(f"Both ({formality_level})", test_text, result, elapsed):
            passed += 1
        else:
            failed += 1

    return passed, failed


def test_connection_health() -> tuple[int, int]:
    """Test connection health and availability."""
    print_section("Connection Health Tests")

    passed = 0
    failed = 0

    # Test 1: Ollama availability
    print("Test: Ollama Service Availability")
    available = check_ollama_available()
    if available:
        print("  [PASS] - Ollama is running\n")
        passed += 1
    else:
        print("  [FAIL] - Ollama is not accessible\n")
        failed += 1

    # Test 2: Model availability
    print("Test: Model List Retrieval")
    models = get_available_models()
    if models and len(models) > 0:
        print(f"  [PASS] - Found {len(models)} models: {', '.join(models)}\n")
        passed += 1
    else:
        print("  [FAIL] - No models found\n")
        failed += 1

    # Test 3: Model connection test
    print("Test: Model Connection (llama3.2:3b)")
    success, message = test_ollama_connection("llama3.2:3b")
    if success:
        print(f"  [PASS] - {message}\n")
        passed += 1
    else:
        print(f"  [FAIL] - {message}\n")
        failed += 1

    return passed, failed


def test_edge_cases() -> tuple[int, int]:
    """Test edge cases and error handling."""
    print_section("Edge Case Tests")

    passed = 0
    failed = 0

    # Test 1: Empty string
    print("Test: Empty String")
    result = cleanup_text("", mode="grammar", model="llama3.2:3b")
    if result is None:
        print("  [PASS] - Returns None for empty string\n")
        passed += 1
    else:
        print("  [FAIL] - Should return None for empty string\n")
        failed += 1

    # Test 2: Very short text
    print("Test: Very Short Text")
    start = time.time()
    result = cleanup_text("ok", mode="grammar", model="llama3.2:3b")
    elapsed = time.time() - start
    # Short text might or might not return a result - just check it doesn't crash
    print(f"  [PASS] - Handled without error (result: '{result}', time: {elapsed:.2f}s)\n")
    passed += 1

    # Test 3: Long text
    print("Test: Longer Text")
    long_text = "hey so i was thinking we could maybe try to do this thing where we work together on the project and i think it would be really cool if we could get this done by the end of the week but i dont know if thats realistic what do you think"
    start = time.time()
    result = cleanup_text(long_text, mode="both", formality_level="professional", model="llama3.2:3b")
    elapsed = time.time() - start

    if print_result("Long Text", long_text[:50] + "...", result, elapsed):
        passed += 1
    else:
        failed += 1

    return passed, failed


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("  OLLAMA AI CLEANUP - LIVE INTEGRATION TESTS")
    print("="*70)
    print("\nTesting against: Ollama service at http://localhost:11434")
    print("Model: llama3.2:3b")

    total_passed = 0
    total_failed = 0

    # Run all test suites
    test_suites = [
        ("Connection Health", test_connection_health),
        ("Grammar Mode", test_grammar_mode),
        ("Formality Mode", test_formality_mode),
        ("Combined Mode", test_both_mode),
        ("Edge Cases", test_edge_cases),
    ]

    for suite_name, test_func in test_suites:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
        except Exception as e:
            print(f"\n- Test suite '{suite_name}' crashed: {e}\n")
            total_failed += 1

    # Print summary
    print_section("Test Summary")
    total = total_passed + total_failed
    pass_rate = (total_passed / total * 100) if total > 0 else 0

    print(f"Total Tests:   {total}")
    print(f"Passed:        {total_passed} +")
    print(f"Failed:        {total_failed} -")
    print(f"Pass Rate:     {pass_rate:.1f}%")
    print()

    if total_failed == 0:
        print("SUCCESS: All tests passed!")
    else:
        print(f"WARNING:  {total_failed} test(s) failed")

    print()

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
