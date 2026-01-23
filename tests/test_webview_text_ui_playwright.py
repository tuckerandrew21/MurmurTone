"""
Playwright UI automation tests for Text settings tab in WebView GUI.

Tests UI interactions including:
- Page visibility and section rendering
- Toggle interactions and state saving
- Nested setting visibility
- Custom filler list management
- Dictionary and shortcuts buttons

NOTE: These tests require the WebView GUI to be running manually:
    cd c:/Users/tucke/Repositories/MurmurTone && py -3.12 settings_webview.py

Then run tests with: pytest tests/test_webview_text_ui_playwright.py -v
"""
import pytest


# =============================================================================
# Test Page Visibility
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestTextPageVisibility:
    """Test that all Text page sections and elements are visible."""

    def test_text_page_loads_all_sections(self, mcp__playwright__browser_evaluate):
        """Verify 4 sections visible: Voice Commands, Filler Removal, Dictionary, Shortcuts."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const page = document.getElementById('page-text');
                const sections = page ? page.querySelectorAll('.settings-section') : [];
                return {
                    pageExists: !!page,
                    sectionCount: sections.length,
                    sections: Array.from(sections).map(s => ({
                        title: s.querySelector('.section-title')?.textContent,
                        description: s.querySelector('.section-description')?.textContent
                    }))
                };
            }"""
        })

        assert result["pageExists"] is True, "Text page should exist"
        assert result["sectionCount"] == 4, "Should have 4 sections: Voice Commands, Filler Removal, Dictionary, Shortcuts"

        section_titles = [s["title"] for s in result["sections"]]
        assert "Voice Commands" in section_titles
        assert "Filler Word Removal" in section_titles
        assert "Custom Dictionary" in section_titles
        assert "Text Shortcuts" in section_titles

    def test_voice_commands_section_complete(self, mcp__playwright__browser_evaluate):
        """Verify Voice Commands section has header, description, 2 toggles."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                return {
                    voiceCommandsExists: !!document.getElementById('voice-commands'),
                    scratchThatExists: !!document.getElementById('scratch-that'),
                    voiceCommandsRow: !!document.getElementById('voice-commands')?.closest('.setting-row'),
                    scratchThatRow: !!document.getElementById('scratch-that-row'),
                    scratchThatNested: document.getElementById('scratch-that-row')?.classList.contains('nested-setting')
                };
            }"""
        })

        assert result["voiceCommandsExists"] is True, "Voice commands toggle should exist"
        assert result["scratchThatExists"] is True, "Scratch that toggle should exist"
        assert result["voiceCommandsRow"] is True, "Voice commands should have setting row"
        assert result["scratchThatRow"] is True, "Scratch that should have its own row"
        assert result["scratchThatNested"] is True, "Scratch that should be marked as nested setting"

    def test_filler_removal_section_complete(self, mcp__playwright__browser_evaluate):
        """Verify Filler Removal section has header, description, 2 toggles, custom list."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                return {
                    fillerRemovalExists: !!document.getElementById('filler-removal'),
                    aggressiveExists: !!document.getElementById('filler-aggressive'),
                    aggressiveNested: document.getElementById('filler-aggressive-row')?.classList.contains('nested-setting'),
                    customSectionExists: !!document.getElementById('custom-fillers-section'),
                    customSectionNested: document.getElementById('custom-fillers-section')?.classList.contains('nested-setting'),
                    fillerInputExists: !!document.getElementById('filler-input'),
                    addButtonExists: !!document.getElementById('add-filler-btn'),
                    searchInputExists: !!document.getElementById('filler-search'),
                    listExists: !!document.getElementById('filler-list'),
                    emptyStateExists: !!document.getElementById('filler-empty')
                };
            }"""
        })

        assert result["fillerRemovalExists"] is True, "Filler removal toggle should exist"
        assert result["aggressiveExists"] is True, "Aggressive mode toggle should exist"
        assert result["aggressiveNested"] is True, "Aggressive mode should be nested setting"
        assert result["customSectionExists"] is True, "Custom fillers section should exist"
        assert result["customSectionNested"] is True, "Custom fillers section should be nested"
        assert result["fillerInputExists"] is True, "Filler input should exist"
        assert result["addButtonExists"] is True, "Add filler button should exist"
        assert result["searchInputExists"] is True, "Search input should exist"
        assert result["listExists"] is True, "Filler list should exist"
        assert result["emptyStateExists"] is True, "Empty state message should exist"

    def test_dictionary_section_has_button(self, mcp__playwright__browser_evaluate):
        """Verify edit-dictionary-btn exists with icon."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const btn = document.getElementById('edit-dictionary-btn');
                return {
                    buttonExists: !!btn,
                    hasIcon: !!btn?.querySelector('svg'),
                    buttonText: btn?.textContent?.trim(),
                    countExists: !!document.getElementById('dictionary-count')
                };
            }"""
        })

        assert result["buttonExists"] is True, "Dictionary button should exist"
        assert result["hasIcon"] is True, "Button should have SVG icon"
        assert "Edit Dictionary" in result["buttonText"], "Button should have correct text"
        assert result["countExists"] is True, "Dictionary count should exist"

    def test_shortcuts_section_has_button(self, mcp__playwright__browser_evaluate):
        """Verify edit-shortcuts-btn exists with icon."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const btn = document.getElementById('edit-shortcuts-btn');
                return {
                    buttonExists: !!btn,
                    hasIcon: !!btn?.querySelector('svg'),
                    buttonText: btn?.textContent?.trim(),
                    countExists: !!document.getElementById('shortcuts-count')
                };
            }"""
        })

        assert result["buttonExists"] is True, "Shortcuts button should exist"
        assert result["hasIcon"] is True, "Button should have SVG icon"
        assert "Edit Shortcuts" in result["buttonText"], "Button should have correct text"
        assert result["countExists"] is True, "Shortcuts count should exist"


# =============================================================================
# Test Toggle Interactions
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestToggleInteractions:
    """Test toggle interactions and nested visibility."""

    def test_voice_commands_toggle_changes_state(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Click toggle, verify checkbox state changes."""
        # Get initial state
        initial = mcp__playwright__browser_evaluate({
            "function": "() => document.getElementById('voice-commands')?.checked"
        })

        # Click the toggle (need to click the label/slider, not the checkbox)
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const checkbox = document.getElementById('voice-commands');
                const initialState = checkbox.checked;
                checkbox.click();
                return {
                    before: initialState,
                    after: checkbox.checked,
                    changed: initialState !== checkbox.checked
                };
            }"""
        })

        assert result["changed"] is True, "Toggle state should change on click"
        assert result["before"] !== result["after"], "State should be different"

    def test_scratch_that_nested_visibility(self, mcp__playwright__browser_evaluate):
        """
        1. Verify scratch-that-row visible when voice-commands on
        2. Toggle voice-commands off
        3. Verify scratch-that-row has .disabled class
        4. Toggle voice-commands back on
        5. Verify .disabled class removed
        """
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const voiceCommands = document.getElementById('voice-commands');
                const scratchRow = document.getElementById('scratch-that-row');

                // Ensure voice commands is ON
                if (!voiceCommands.checked) {
                    voiceCommands.click();
                }
                const step1_enabled = voiceCommands.checked;
                const step1_disabled = scratchRow.classList.contains('disabled');

                // Turn OFF voice commands
                voiceCommands.click();
                const step2_enabled = voiceCommands.checked;
                const step2_disabled = scratchRow.classList.contains('disabled');

                // Turn ON voice commands again
                voiceCommands.click();
                const step3_enabled = voiceCommands.checked;
                const step3_disabled = scratchRow.classList.contains('disabled');

                return {
                    step1: { enabled: step1_enabled, disabled: step1_disabled },
                    step2: { enabled: step2_enabled, disabled: step2_disabled },
                    step3: { enabled: step3_enabled, disabled: step3_disabled }
                };
            }"""
        })

        # Step 1: Voice commands ON, scratch-that should NOT be disabled
        assert result["step1"]["enabled"] is True, "Voice commands should be ON"
        assert result["step1"]["disabled"] is False, "Scratch-that should NOT have disabled class when parent ON"

        # Step 2: Voice commands OFF, scratch-that should be disabled
        assert result["step2"]["enabled"] is False, "Voice commands should be OFF"
        assert result["step2"]["disabled"] is True, "Scratch-that SHOULD have disabled class when parent OFF"

        # Step 3: Voice commands ON again, scratch-that should NOT be disabled
        assert result["step3"]["enabled"] is True, "Voice commands should be ON again"
        assert result["step3"]["disabled"] is False, "Scratch-that should NOT have disabled class when parent ON"

    def test_filler_removal_toggle_changes_state(self, mcp__playwright__browser_evaluate):
        """Click toggle, verify checkbox state changes."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const checkbox = document.getElementById('filler-removal');
                const initialState = checkbox.checked;
                checkbox.click();
                return {
                    before: initialState,
                    after: checkbox.checked,
                    changed: initialState !== checkbox.checked
                };
            }"""
        })

        assert result["changed"] is True, "Toggle state should change on click"

    def test_aggressive_mode_nested_visibility(self, mcp__playwright__browser_evaluate):
        """Similar to scratch-that test - verify conditional disabling."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const fillerRemoval = document.getElementById('filler-removal');
                const aggressiveRow = document.getElementById('filler-aggressive-row');

                // Ensure filler removal is ON
                if (!fillerRemoval.checked) {
                    fillerRemoval.click();
                }
                const step1_enabled = fillerRemoval.checked;
                const step1_disabled = aggressiveRow.classList.contains('disabled');

                // Turn OFF filler removal
                fillerRemoval.click();
                const step2_enabled = fillerRemoval.checked;
                const step2_disabled = aggressiveRow.classList.contains('disabled');

                // Turn ON filler removal again
                fillerRemoval.click();
                const step3_enabled = fillerRemoval.checked;
                const step3_disabled = aggressiveRow.classList.contains('disabled');

                return {
                    step1: { enabled: step1_enabled, disabled: step1_disabled },
                    step2: { enabled: step2_enabled, disabled: step2_disabled },
                    step3: { enabled: step3_enabled, disabled: step3_disabled }
                };
            }"""
        })

        assert result["step1"]["disabled"] is False, "Aggressive mode should NOT be disabled when filler removal ON"
        assert result["step2"]["disabled"] is True, "Aggressive mode SHOULD be disabled when filler removal OFF"
        assert result["step3"]["disabled"] is False, "Aggressive mode should NOT be disabled when filler removal ON again"

    def test_custom_fillers_section_nested_visibility(self, mcp__playwright__browser_evaluate):
        """Verify entire custom-fillers-section disabled when filler-removal off."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const fillerRemoval = document.getElementById('filler-removal');
                const customSection = document.getElementById('custom-fillers-section');

                // Ensure filler removal is ON
                if (!fillerRemoval.checked) {
                    fillerRemoval.click();
                }
                const step1_disabled = customSection.classList.contains('disabled');

                // Turn OFF filler removal
                fillerRemoval.click();
                const step2_disabled = customSection.classList.contains('disabled');

                // Turn ON filler removal again
                fillerRemoval.click();
                const step3_disabled = customSection.classList.contains('disabled');

                return {
                    step1_disabled: step1_disabled,
                    step2_disabled: step2_disabled,
                    step3_disabled: step3_disabled
                };
            }"""
        })

        assert result["step1_disabled"] is False, "Custom fillers section should NOT be disabled when filler removal ON"
        assert result["step2_disabled"] is True, "Custom fillers section SHOULD be disabled when filler removal OFF"
        assert result["step3_disabled"] is False, "Custom fillers section should NOT be disabled when filler removal ON again"


# =============================================================================
# Test Custom Filler List
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestCustomFillerList:
    """Test custom filler word list management."""

    def test_add_filler_word_via_button(self, mcp__playwright__browser_evaluate):
        """Type 'basically' in filler-input, click add-filler-btn, verify added."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const input = document.getElementById('filler-input');
                const addBtn = document.getElementById('add-filler-btn');
                const list = document.getElementById('filler-list');

                // Get initial count
                const initialCount = list.children.length;

                // Type word and click add
                input.value = 'basically';
                addBtn.click();

                // Wait a bit for async operation
                return new Promise(resolve => {
                    setTimeout(() => {
                        const finalCount = list.children.length;
                        const items = Array.from(list.children).map(li => li.textContent);
                        resolve({
                            initialCount: initialCount,
                            finalCount: finalCount,
                            added: finalCount > initialCount,
                            items: items,
                            hasBasically: items.some(text => text.includes('basically'))
                        });
                    }, 500);
                });
            }"""
        })

        assert result["added"] is True, "Item count should increase"
        assert result["hasBasically"] is True, "List should contain 'basically'"

    def test_add_filler_word_via_enter_key(self, mcp__playwright__browser_evaluate):
        """Type 'basically', press Enter, verify added."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const input = document.getElementById('filler-input');
                const list = document.getElementById('filler-list');

                const initialCount = list.children.length;

                // Type word and press Enter
                input.value = 'actually';
                const event = new KeyboardEvent('keypress', { key: 'Enter' });
                input.dispatchEvent(event);

                return new Promise(resolve => {
                    setTimeout(() => {
                        const finalCount = list.children.length;
                        const items = Array.from(list.children).map(li => li.textContent);
                        resolve({
                            initialCount: initialCount,
                            finalCount: finalCount,
                            added: finalCount > initialCount,
                            items: items,
                            hasActually: items.some(text => text.includes('actually'))
                        });
                    }, 500);
                });
            }"""
        })

        assert result["added"] is True, "Item count should increase"
        assert result["hasActually"] is True, "List should contain 'actually'"

    def test_add_uppercase_normalizes_to_lowercase(self, mcp__playwright__browser_evaluate):
        """Type 'BASICALLY', verify saved as 'basically'."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const input = document.getElementById('filler-input');
                const addBtn = document.getElementById('add-filler-btn');
                const list = document.getElementById('filler-list');

                input.value = 'BASICALLY';
                addBtn.click();

                return new Promise(resolve => {
                    setTimeout(() => {
                        const items = Array.from(list.children).map(li => li.textContent);
                        resolve({
                            items: items,
                            hasLowercase: items.some(text => text.includes('basically')),
                            hasUppercase: items.some(text => text.includes('BASICALLY'))
                        });
                    }, 500);
                });
            }"""
        })

        assert result["hasLowercase"] is True, "Should normalize to lowercase 'basically'"
        assert result["hasUppercase"] is False, "Should NOT keep uppercase 'BASICALLY'"

    def test_add_whitespace_trimmed(self, mcp__playwright__browser_evaluate):
        """Type ' um  ', verify saved as 'um'."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const input = document.getElementById('filler-input');
                const addBtn = document.getElementById('add-filler-btn');
                const list = document.getElementById('filler-list');

                input.value = '  umm  ';
                addBtn.click();

                return new Promise(resolve => {
                    setTimeout(() => {
                        const items = Array.from(list.children).map(li => li.textContent.trim());
                        resolve({
                            items: items,
                            hasTrimmed: items.some(text => text.match(/^umm$/))
                        });
                    }, 500);
                });
            }"""
        })

        assert result["hasTrimmed"] is True, "Should trim whitespace to 'umm'"

    def test_remove_filler_word(self, mcp__playwright__browser_evaluate):
        """Add 'like', click remove button, verify removed from list."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const input = document.getElementById('filler-input');
                const addBtn = document.getElementById('add-filler-btn');
                const list = document.getElementById('filler-list');

                // Add the word
                input.value = 'testword';
                addBtn.click();

                return new Promise(resolve => {
                    setTimeout(() => {
                        const beforeCount = list.children.length;
                        const beforeItems = Array.from(list.children).map(li => li.textContent);

                        // Find and click remove button for 'testword'
                        const items = list.querySelectorAll('li');
                        let removed = false;
                        items.forEach(li => {
                            if (li.textContent.includes('testword')) {
                                const removeBtn = li.querySelector('button');
                                if (removeBtn) {
                                    removeBtn.click();
                                    removed = true;
                                }
                            }
                        });

                        setTimeout(() => {
                            const afterCount = list.children.length;
                            const afterItems = Array.from(list.children).map(li => li.textContent);
                            resolve({
                                beforeCount: beforeCount,
                                afterCount: afterCount,
                                removed: removed,
                                decreased: afterCount < beforeCount,
                                stillHasWord: afterItems.some(text => text.includes('testword'))
                            });
                        }, 500);
                    }, 500);
                });
            }"""
        })

        assert result["removed"] is True, "Should have found and clicked remove button"
        assert result["decreased"] is True, "Item count should decrease"
        assert result["stillHasWord"] is False, "Word should be removed from list"

    def test_filler_empty_state_visible_when_empty(self, mcp__playwright__browser_evaluate):
        """Verify filler-empty visible when list empty, hidden when populated."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const list = document.getElementById('filler-list');
                const emptyState = document.getElementById('filler-empty');

                return {
                    listCount: list.children.length,
                    emptyStateHidden: emptyState.classList.contains('hidden'),
                    shouldBeHidden: list.children.length > 0
                };
            }"""
        })

        if result["listCount"] == 0:
            assert result["emptyStateHidden"] is False, "Empty state should be visible when list is empty"
        else:
            assert result["emptyStateHidden"] is True, "Empty state should be hidden when list has items"


# =============================================================================
# Test Dictionary and Shortcuts
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestDictionaryAndShortcuts:
    """Test dictionary and shortcuts buttons."""

    def test_dictionary_button_exists_and_clickable(self, mcp__playwright__browser_evaluate):
        """Verify edit-dictionary-btn exists and responds to click."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const btn = document.getElementById('edit-dictionary-btn');
                return {
                    exists: !!btn,
                    clickable: !btn?.disabled,
                    visible: btn?.offsetParent !== null
                };
            }"""
        })

        assert result["exists"] is True, "Dictionary button should exist"
        assert result["clickable"] is True, "Dictionary button should be clickable"
        assert result["visible"] is True, "Dictionary button should be visible"

    def test_dictionary_count_displays_correctly(self, mcp__playwright__browser_evaluate):
        """Verify dictionary-count shows correct text."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const count = document.getElementById('dictionary-count');
                return {
                    exists: !!count,
                    text: count?.textContent?.trim()
                };
            }"""
        })

        assert result["exists"] is True, "Dictionary count element should exist"
        assert "replacements defined" in result["text"], "Count should show 'replacements defined' text"

    def test_shortcuts_button_exists_and_clickable(self, mcp__playwright__browser_evaluate):
        """Verify edit-shortcuts-btn exists and responds to click."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const btn = document.getElementById('edit-shortcuts-btn');
                return {
                    exists: !!btn,
                    clickable: !btn?.disabled,
                    visible: btn?.offsetParent !== null
                };
            }"""
        })

        assert result["exists"] is True, "Shortcuts button should exist"
        assert result["clickable"] is True, "Shortcuts button should be clickable"
        assert result["visible"] is True, "Shortcuts button should be visible"

    def test_shortcuts_count_displays_correctly(self, mcp__playwright__browser_evaluate):
        """Verify shortcuts-count shows correct text."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const count = document.getElementById('shortcuts-count');
                return {
                    exists: !!count,
                    text: count?.textContent?.trim()
                };
            }"""
        })

        assert result["exists"] is True, "Shortcuts count element should exist"
        assert "shortcuts defined" in result["text"], "Count should show 'shortcuts defined' text"
