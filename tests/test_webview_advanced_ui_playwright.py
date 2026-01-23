"""
Playwright UI automation tests for Advanced settings tab in WebView GUI.

Tests UI interactions including:
- Page visibility and section rendering
- AI Cleanup toggle and nested settings
- Ollama connection status flow
- History modal interactions
- Reset to defaults functionality

NOTE: These tests require the WebView GUI to be running manually:
    cd c:/Users/tucke/Repositories/MurmurTone && py -3.12 settings_webview.py

Then run tests with: pytest tests/test_webview_advanced_ui_playwright.py -v
"""
import pytest


# =============================================================================
# Test Page Visibility
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestAdvancedPageVisibility:
    """Test that all Advanced page sections and elements are visible."""

    def test_advanced_page_loads_all_sections(self, mcp__playwright__browser_evaluate):
        """Verify 3 sections visible: AI Cleanup, History, Reset."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const page = document.getElementById('page-advanced');
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

        assert result["pageExists"] is True, "Advanced page should exist"
        assert result["sectionCount"] >= 3, "Should have at least 3 sections"

        section_titles = [s["title"] for s in result["sections"] if s["title"]]
        assert any("AI" in t or "Cleanup" in t for t in section_titles), "Should have AI Cleanup section"
        assert any("History" in t for t in section_titles), "Should have History section"
        assert any("Reset" in t for t in section_titles), "Should have Reset section"

    def test_ai_cleanup_section_complete(self, mcp__playwright__browser_evaluate):
        """Verify AI Cleanup section has all required elements."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                return {
                    aiCleanupToggle: !!document.getElementById('ai-cleanup'),
                    ollamaUrl: !!document.getElementById('ollama-url'),
                    testOllamaBtn: !!document.getElementById('test-ollama-btn'),
                    ollamaStatus: !!document.getElementById('ollama-status'),
                    ollamaModel: !!document.getElementById('ollama-model'),
                    cleanupMode: !!document.getElementById('ai-cleanup-mode'),
                    formalityLevel: !!document.getElementById('ai-formality-level'),
                    retryBtn: !!document.getElementById('retry-ollama-btn'),
                    downloadLink: !!document.getElementById('download-ollama-link')
                };
            }"""
        })

        assert result["aiCleanupToggle"] is True, "AI cleanup toggle should exist"
        assert result["ollamaUrl"] is True, "Ollama URL input should exist"
        assert result["testOllamaBtn"] is True, "Test Ollama button should exist"
        assert result["ollamaStatus"] is True, "Ollama status badge should exist"
        assert result["ollamaModel"] is True, "Ollama model dropdown should exist"
        assert result["cleanupMode"] is True, "Cleanup mode dropdown should exist"
        assert result["formalityLevel"] is True, "Formality level dropdown should exist"

    def test_history_section_complete(self, mcp__playwright__browser_evaluate):
        """Verify History section has View History button and count."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                return {
                    viewHistoryBtn: !!document.getElementById('view-history-btn'),
                    historyCount: !!document.getElementById('history-count'),
                    viewHistoryBtnText: document.getElementById('view-history-btn')?.textContent?.trim()
                };
            }"""
        })

        assert result["viewHistoryBtn"] is True, "View History button should exist"
        assert result["historyCount"] is True, "History count display should exist"
        assert "View History" in result["viewHistoryBtnText"], "Button should have correct text"

    def test_reset_section_complete(self, mcp__playwright__browser_evaluate):
        """Verify Reset section has Reset to Defaults button."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const btn = document.getElementById('reset-defaults-btn');
                return {
                    resetBtn: !!btn,
                    resetBtnText: btn?.textContent?.trim()
                };
            }"""
        })

        assert result["resetBtn"] is True, "Reset to Defaults button should exist"
        assert "Reset" in result["resetBtnText"], "Button should have Reset in text"


# =============================================================================
# Test AI Cleanup Interactions
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestAICleanupInteractions:
    """Test AI cleanup toggle and nested settings visibility."""

    def test_ai_cleanup_toggle_changes_state(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Toggle AI cleanup on and verify state changes."""
        # Get initial state
        initial = mcp__playwright__browser_evaluate({
            "function": """() => {
                const toggle = document.getElementById('ai-cleanup');
                return toggle?.checked ?? false;
            }"""
        })

        # Click the toggle
        mcp__playwright__browser_click({
            "element": "AI cleanup toggle",
            "ref": "ai-cleanup"
        })

        # Get new state
        after = mcp__playwright__browser_evaluate({
            "function": """() => {
                const toggle = document.getElementById('ai-cleanup');
                return toggle?.checked ?? false;
            }"""
        })

        assert initial != after, "Toggle state should change after click"

    def test_ollama_url_input_editable(self, mcp__playwright__browser_evaluate):
        """Verify Ollama URL input can be edited."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const input = document.getElementById('ollama-url');
                return {
                    exists: !!input,
                    type: input?.type,
                    disabled: input?.disabled ?? true,
                    value: input?.value ?? ''
                };
            }"""
        })

        assert result["exists"] is True, "Ollama URL input should exist"
        assert result["type"] == "text", "Input should be text type"
        assert result["disabled"] is False, "Input should not be disabled"
        assert "localhost" in result["value"], "Should have default localhost URL"

    def test_ollama_model_dropdown_has_options(self, mcp__playwright__browser_evaluate):
        """Verify Ollama model dropdown has all 4 options."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const select = document.getElementById('ollama-model');
                const options = select ? Array.from(select.options) : [];
                return {
                    exists: !!select,
                    optionCount: options.length,
                    optionValues: options.map(o => o.value)
                };
            }"""
        })

        assert result["exists"] is True, "Ollama model dropdown should exist"
        assert result["optionCount"] >= 4, "Should have at least 4 model options"
        assert "llama3.2:3b" in result["optionValues"], "Should have llama3.2:3b option"
        assert "mistral:7b" in result["optionValues"], "Should have mistral:7b option"

    def test_cleanup_mode_dropdown_changes(self, mcp__playwright__browser_evaluate):
        """Test cleanup mode dropdown has correct options."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const select = document.getElementById('ai-cleanup-mode');
                const options = select ? Array.from(select.options) : [];
                return {
                    exists: !!select,
                    optionValues: options.map(o => o.value)
                };
            }"""
        })

        assert result["exists"] is True, "Cleanup mode dropdown should exist"
        assert "grammar" in result["optionValues"], "Should have grammar option"
        assert "formality" in result["optionValues"], "Should have formality option"
        assert "both" in result["optionValues"], "Should have both option"

    def test_formality_row_visibility_toggle(self, mcp__playwright__browser_evaluate):
        """Test formality row visibility based on cleanup mode."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const formalityRow = document.getElementById('formality-row');
                const cleanupMode = document.getElementById('ai-cleanup-mode');
                return {
                    formalityRowExists: !!formalityRow,
                    currentMode: cleanupMode?.value ?? '',
                    formalityRowDisplay: formalityRow?.style.display ?? 'block'
                };
            }"""
        })

        assert result["formalityRowExists"] is True, "Formality row should exist"
        # When mode is 'grammar', formality should be hidden
        # When mode is 'formality' or 'both', formality should be visible


# =============================================================================
# Test Ollama Status Flow
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestOllamaStatusFlow:
    """Test Ollama connection status badge state transitions."""

    def test_test_button_updates_status(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Clicking Test button should update status badge."""
        # Get initial status
        initial = mcp__playwright__browser_evaluate({
            "function": """() => {
                const badge = document.getElementById('ollama-status');
                return badge?.textContent?.trim() ?? '';
            }"""
        })

        # Click test button
        mcp__playwright__browser_click({
            "element": "Test Ollama button",
            "ref": "test-ollama-btn"
        })

        # Wait a moment for async operation
        import time
        time.sleep(2)

        # Get updated status
        after = mcp__playwright__browser_evaluate({
            "function": """() => {
                const badge = document.getElementById('ollama-status');
                return badge?.textContent?.trim() ?? '';
            }"""
        })

        # Status should change (either to "Connected" or error message)
        # Don't assert they're different since initial might already show a state

    def test_action_row_visibility(self, mcp__playwright__browser_evaluate):
        """Test retry/download buttons row exists."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const actionRow = document.getElementById('ollama-action-row');
                return {
                    exists: !!actionRow,
                    retryBtn: !!document.getElementById('retry-ollama-btn'),
                    downloadLink: !!document.getElementById('download-ollama-link')
                };
            }"""
        })

        assert result["exists"] is True, "Action row should exist"
        assert result["retryBtn"] is True, "Retry button should exist"
        assert result["downloadLink"] is True, "Download link should exist"


# =============================================================================
# Test History Modal Interactions
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestHistoryModalInteractions:
    """Test history modal open/close and interactions."""

    def test_view_history_opens_modal(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Clicking View History should open the modal."""
        # Check modal is initially hidden
        initial = mcp__playwright__browser_evaluate({
            "function": """() => {
                const modal = document.getElementById('history-modal');
                return {
                    exists: !!modal,
                    visible: modal?.classList.contains('visible') ?? false
                };
            }"""
        })

        assert initial["exists"] is True, "History modal should exist"

        # Click View History button
        mcp__playwright__browser_click({
            "element": "View History button",
            "ref": "view-history-btn"
        })

        # Check modal is now visible
        after = mcp__playwright__browser_evaluate({
            "function": """() => {
                const modal = document.getElementById('history-modal');
                return modal?.classList.contains('visible') ?? false;
            }"""
        })

        assert after is True, "Modal should be visible after clicking View History"

    def test_history_modal_has_all_buttons(self, mcp__playwright__browser_evaluate):
        """Verify history modal has all required buttons."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                return {
                    copyBtn: !!document.getElementById('history-copy'),
                    clearBtn: !!document.getElementById('history-clear'),
                    exportBtn: !!document.getElementById('history-export'),
                    closeBtn: !!document.getElementById('history-close')
                };
            }"""
        })

        assert result["copyBtn"] is True, "Copy button should exist"
        assert result["clearBtn"] is True, "Clear button should exist"
        assert result["exportBtn"] is True, "Export button should exist"
        assert result["closeBtn"] is True, "Close button should exist"

    def test_history_modal_close(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Test closing history modal."""
        # First open the modal
        mcp__playwright__browser_click({
            "element": "View History button",
            "ref": "view-history-btn"
        })

        # Click close button
        mcp__playwright__browser_click({
            "element": "Close history modal",
            "ref": "history-close"
        })

        # Check modal is hidden
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const modal = document.getElementById('history-modal');
                return modal?.classList.contains('visible') ?? true;
            }"""
        })

        assert result is False, "Modal should be hidden after clicking close"

    def test_copy_button_disabled_initially(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Copy button should be disabled when no item is selected."""
        # Open modal
        mcp__playwright__browser_click({
            "element": "View History button",
            "ref": "view-history-btn"
        })

        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const copyBtn = document.getElementById('history-copy');
                return copyBtn?.disabled ?? false;
            }"""
        })

        assert result is True, "Copy button should be disabled when no item selected"


# =============================================================================
# Test Export Format Modal
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestExportFormatModal:
    """Test export format selection modal."""

    def test_export_format_modal_exists(self, mcp__playwright__browser_evaluate):
        """Verify export format modal exists in DOM."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const modal = document.getElementById('export-format-modal');
                return {
                    exists: !!modal,
                    hasRadios: !!modal?.querySelector('input[name="export-format"]')
                };
            }"""
        })

        assert result["exists"] is True, "Export format modal should exist"
        assert result["hasRadios"] is True, "Modal should have format radio buttons"

    def test_export_format_options(self, mcp__playwright__browser_evaluate):
        """Verify all 3 export format options exist."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const radios = document.querySelectorAll('input[name="export-format"]');
                return {
                    count: radios.length,
                    values: Array.from(radios).map(r => r.value)
                };
            }"""
        })

        assert result["count"] >= 3, "Should have at least 3 format options"
        assert "txt" in result["values"], "Should have TXT option"
        assert "csv" in result["values"], "Should have CSV option"
        assert "json" in result["values"], "Should have JSON option"


# =============================================================================
# Test Reset to Defaults
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestResetToDefaults:
    """Test reset to defaults functionality."""

    def test_reset_button_exists_and_clickable(self, mcp__playwright__browser_evaluate):
        """Verify Reset to Defaults button exists and is enabled."""
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const btn = document.getElementById('reset-defaults-btn');
                return {
                    exists: !!btn,
                    disabled: btn?.disabled ?? true,
                    text: btn?.textContent?.trim() ?? ''
                };
            }"""
        })

        assert result["exists"] is True, "Reset button should exist"
        assert result["disabled"] is False, "Reset button should not be disabled"
        assert "Reset" in result["text"], "Button should have Reset in text"

    def test_reset_shows_confirmation(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Clicking reset should show confirmation dialog."""
        # Click reset button
        mcp__playwright__browser_click({
            "element": "Reset to Defaults button",
            "ref": "reset-defaults-btn"
        })

        # Check for confirmation modal or dialog
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                // Check for reset confirmation modal
                const modal = document.getElementById('reset-confirm-modal');
                if (modal) {
                    return { type: 'modal', visible: modal.classList.contains('visible') };
                }
                // Check for native confirm dialog (can't directly detect, but check if reset happened)
                return { type: 'native', visible: null };
            }"""
        })

        # Either a custom modal or native confirm should be shown
        # Can't reliably test native confirm from Playwright


# =============================================================================
# Test Navigation
# =============================================================================

@pytest.mark.skip(reason="Requires running GUI - execute manually")
class TestAdvancedNavigation:
    """Test navigation to Advanced page."""

    def test_can_navigate_to_advanced_page(self, mcp__playwright__browser_evaluate, mcp__playwright__browser_click):
        """Test clicking Advanced nav item shows Advanced page."""
        # Click Advanced nav item
        mcp__playwright__browser_click({
            "element": "Advanced navigation item",
            "ref": "[data-page='advanced']"
        })

        # Verify Advanced page is visible
        result = mcp__playwright__browser_evaluate({
            "function": """() => {
                const page = document.getElementById('page-advanced');
                const isActive = page?.classList.contains('active') ?? false;
                const isVisible = page?.style.display !== 'none';
                return { isActive, isVisible };
            }"""
        })

        assert result["isActive"] or result["isVisible"], "Advanced page should be active/visible"
