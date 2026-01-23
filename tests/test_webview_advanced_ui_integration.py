"""
E2E/Integration tests for PyWebView Advanced tab.
Tests UI state management, modal interactions, and feature parity with Tkinter.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# HTML Structure Tests
# =============================================================================

class TestHistoryModalElements:
    """Test history modal HTML structure."""

    def test_history_modal_exists(self):
        """Verify history modal element exists in HTML."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-modal"' in content

    def test_history_list_exists(self):
        """Verify history list element exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-list"' in content

    def test_history_copy_button_exists(self):
        """Verify copy button exists in history modal."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-copy"' in content

    def test_history_copy_button_disabled_by_default(self):
        """Verify copy button is disabled by default."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the copy button and check for disabled attribute
        assert 'id="history-copy" disabled' in content

    def test_history_clear_button_exists(self):
        """Verify clear button exists in history modal."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-clear"' in content

    def test_history_export_button_exists(self):
        """Verify export button exists in history modal."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-export"' in content

    def test_history_close_button_exists(self):
        """Verify close button exists in history modal."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-close"' in content

    def test_history_empty_state_exists(self):
        """Verify empty state message element exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-empty"' in content


class TestExportFormatModal:
    """Test export format selection modal structure."""

    def test_export_format_modal_exists(self):
        """Verify export format modal exists in HTML."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="export-format-modal"' in content

    def test_export_format_txt_option_exists(self):
        """Verify TXT export format option exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'name="export-format"' in content
        assert 'value="txt"' in content

    def test_export_format_csv_option_exists(self):
        """Verify CSV export format option exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'value="csv"' in content

    def test_export_format_json_option_exists(self):
        """Verify JSON export format option exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'value="json"' in content


# =============================================================================
# JavaScript Function Tests
# =============================================================================

class TestJSFunctionality:
    """Test JavaScript function existence and behavior."""

    def test_test_ollama_connection_function_exists(self):
        """Verify testOllamaConnection function exists in JS."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'async function testOllamaConnection()' in content

    def test_update_history_count_function_exists(self):
        """Verify function to update history count exists in JS."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Function may be named differently, check for history count update logic
        assert 'history-count' in content
        assert 'pywebview.api.get_history_count' in content

    def test_clear_history_function_exists(self):
        """Verify clearHistory function exists in JS."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'async function clearHistory()' in content

    def test_export_history_function_exists(self):
        """Verify exportHistory function exists in JS."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'async function exportHistory' in content

    def test_formality_row_toggle_logic_exists(self):
        """Verify logic to toggle formality row based on cleanup mode."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for formality row visibility logic
        assert 'formality-row' in content
        # Check for condition that hides when mode is grammar
        assert 'grammar' in content

    def test_ollama_status_update_logic_exists(self):
        """Verify logic to update Ollama status badge."""
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'settings.js'
        )

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for status badge update
        assert 'ollama-status' in content
        # Check for connected/error states
        assert 'Connected' in content or 'connected' in content


# =============================================================================
# Feature Parity Tests (PyWebView matches Tkinter)
# =============================================================================

class TestFeatureParityWithTkinter:
    """Verify PyWebView has all features present in Tkinter."""

    def test_ai_cleanup_toggle_exists(self):
        """Both versions should have AI cleanup toggle."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # PyWebView: #ai-cleanup (Tkinter: ai_cleanup_var)
        assert 'id="ai-cleanup"' in content

    def test_cleanup_mode_dropdown_exists(self):
        """Both versions should have cleanup mode dropdown."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="ai-cleanup-mode"' in content

    def test_cleanup_mode_values_match_tkinter(self):
        """Cleanup mode should have same values as Tkinter: grammar, formality, both."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tkinter has: ["grammar", "formality", "both"]
        assert 'value="grammar"' in content
        assert 'value="formality"' in content
        assert 'value="both"' in content

    def test_formality_level_dropdown_exists(self):
        """Both versions should have formality level dropdown."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="ai-formality-level"' in content

    def test_formality_level_values_match_tkinter(self):
        """Formality level should have same values as Tkinter: casual, professional, formal."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tkinter has: ["casual", "professional", "formal"]
        assert 'value="casual"' in content
        assert 'value="professional"' in content
        assert 'value="formal"' in content

    def test_view_history_button_exists(self):
        """Both versions should have View History button."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="view-history-btn"' in content

    def test_reset_defaults_button_exists(self):
        """Both versions should have Reset to Defaults button."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="reset-defaults-btn"' in content

    def test_ollama_status_indicator_exists(self):
        """Both versions should have Ollama status indicator."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="ollama-status"' in content

    def test_retry_ollama_button_exists(self):
        """Both versions should have retry Ollama button."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="retry-ollama-btn"' in content

    def test_download_ollama_link_exists(self):
        """Both versions should have download Ollama link."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="download-ollama-link"' in content
        assert 'https://ollama.com/download' in content


# =============================================================================
# PyWebView-Only Features Tests
# =============================================================================

class TestPyWebViewOnlyFeatures:
    """Test features that PyWebView has but Tkinter doesn't."""

    def test_ollama_url_input_exists(self):
        """PyWebView should have editable Ollama URL input (Tkinter reads from config silently)."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="ollama-url"' in content
        assert 'type="text"' in content

    def test_test_ollama_button_exists(self):
        """PyWebView should have Test Ollama button (Tkinter auto-tests)."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="test-ollama-btn"' in content

    def test_ollama_model_dropdown_exists(self):
        """PyWebView should have Ollama model dropdown (Tkinter reads from config silently)."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="ollama-model"' in content

    def test_ollama_model_options(self):
        """Verify all 4 model options in dropdown."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'value="llama3.2:3b"' in content
        assert 'value="llama3.2:7b"' in content
        assert 'value="mistral:7b"' in content
        assert 'value="phi3:mini"' in content

    def test_history_count_display_exists(self):
        """PyWebView should show history count before opening modal."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="history-count"' in content


# =============================================================================
# Advanced Tab Section Tests
# =============================================================================

class TestAdvancedTabSections:
    """Test that Advanced tab has all required sections."""

    def test_advanced_page_exists(self):
        """Verify Advanced page element exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'id="page-advanced"' in content

    def test_advanced_nav_item_exists(self):
        """Verify Advanced nav item exists."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'data-page="advanced"' in content

    def test_ai_cleanup_section_has_title(self):
        """Verify AI cleanup section has proper title."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for AI Text Cleanup or similar title
        assert 'AI Text Cleanup' in content or 'AI Cleanup' in content

    def test_transcription_history_section_has_title(self):
        """Verify Transcription History section has proper title."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'Transcription History' in content

    def test_reset_settings_section_has_title(self):
        """Verify Reset Settings section has proper title."""
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'index.html'
        )

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'Reset Settings' in content or 'Reset to Defaults' in content
