"""
Test script to verify all dropdowns are in readonly state.
This checks that all CTkComboBox widgets have state='readonly'.
"""
import re
import sys


def check_dropdowns_readonly():
    """Check that all ComboBox instances have state='readonly'."""
    with open('settings_gui.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all CTkComboBox instances
    pattern = r'ctk\.CTkComboBox\((.*?)\)'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    print(f"Found {len(matches)} CTkComboBox instances")
    print("-" * 60)

    all_readonly = True
    for i, match in enumerate(matches, 1):
        combobox_code = match.group(1)
        line_num = content[:match.start()].count('\n') + 1

        # Check if state="readonly" is present
        has_readonly = 'state="readonly"' in combobox_code

        # Extract a brief identifier (variable name or description)
        var_match = re.search(r'variable=(\w+)', combobox_code)
        identifier = var_match.group(1) if var_match else f"line {line_num}"

        status = "[OK] READONLY" if has_readonly else "[FAIL] MISSING"
        print(f"{i}. {identifier:30s} {status}")

        if not has_readonly:
            all_readonly = False

    print("-" * 60)
    if all_readonly:
        print("SUCCESS: All dropdowns are readonly!")
        return 0
    else:
        print("FAILURE: Some dropdowns are missing readonly state")
        return 1


if __name__ == "__main__":
    sys.exit(check_dropdowns_readonly())
