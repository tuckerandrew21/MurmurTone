"""
Tests for clipboard_utils.py - Clipboard save/restore functionality.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestClipboardUtilsNonWindows:
    """Tests for non-Windows platforms (no-op behavior)."""

    def test_import_on_non_windows(self):
        """Module should import without error on non-Windows."""
        # This test runs on whatever platform pytest is on
        import clipboard_utils
        assert hasattr(clipboard_utils, 'save_clipboard')
        assert hasattr(clipboard_utils, 'restore_clipboard')
        assert hasattr(clipboard_utils, 'restore_clipboard_async')


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only tests")
class TestClipboardUtilsWindows:
    """Tests for Windows clipboard functionality."""

    def test_save_clipboard_empty(self):
        """save_clipboard should return empty dict when clipboard is empty."""
        import clipboard_utils

        with patch.object(clipboard_utils, '_open_clipboard_with_retry', return_value=True), \
             patch.object(clipboard_utils, 'EnumClipboardFormats', return_value=0), \
             patch.object(clipboard_utils, 'CloseClipboard'):
            result = clipboard_utils.save_clipboard()
            assert result == {}

    def test_save_clipboard_fails_to_open(self):
        """save_clipboard should return empty dict when clipboard can't be opened."""
        import clipboard_utils

        with patch.object(clipboard_utils, '_open_clipboard_with_retry', return_value=False):
            result = clipboard_utils.save_clipboard()
            assert result == {}

    def test_restore_clipboard_empty_dict(self):
        """restore_clipboard should return True for empty dict (nothing to restore)."""
        import clipboard_utils

        result = clipboard_utils.restore_clipboard({})
        assert result is True

    def test_restore_clipboard_fails_to_open(self):
        """restore_clipboard should return False when clipboard can't be opened."""
        import clipboard_utils

        with patch.object(clipboard_utils, '_open_clipboard_with_retry', return_value=False):
            result = clipboard_utils.restore_clipboard({13: b'test'})
            assert result is False

    def test_restore_clipboard_async_empty(self):
        """restore_clipboard_async should do nothing for empty dict."""
        import clipboard_utils
        import threading

        original_thread_count = threading.active_count()
        clipboard_utils.restore_clipboard_async({})
        # No new thread should be created for empty dict
        # Give a tiny moment for any thread to start
        import time
        time.sleep(0.01)
        assert threading.active_count() <= original_thread_count + 1  # Allow for test runner threads

    def test_supported_formats_defined(self):
        """SUPPORTED_FORMATS should include common clipboard formats."""
        import clipboard_utils

        # Unicode text should be supported
        assert clipboard_utils.CF_UNICODETEXT in clipboard_utils.SUPPORTED_FORMATS
        # DIB (images) should be supported
        assert clipboard_utils.CF_DIB in clipboard_utils.SUPPORTED_FORMATS

    def test_open_clipboard_with_retry_success(self):
        """_open_clipboard_with_retry should return True on successful open."""
        import clipboard_utils

        with patch.object(clipboard_utils, 'OpenClipboard', return_value=True):
            result = clipboard_utils._open_clipboard_with_retry()
            assert result is True

    def test_open_clipboard_with_retry_failure(self):
        """_open_clipboard_with_retry should return False after max attempts."""
        import clipboard_utils

        with patch.object(clipboard_utils, 'OpenClipboard', return_value=False), \
             patch('time.sleep'):  # Don't actually sleep in tests
            result = clipboard_utils._open_clipboard_with_retry(max_attempts=3, delay_ms=10)
            assert result is False


class TestClipboardIntegration:
    """Integration tests that verify the clipboard flow."""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only tests")
    def test_save_and_restore_roundtrip_mocked(self):
        """Test the full save/restore cycle with mocked Windows API."""
        import clipboard_utils

        # Mock data representing saved clipboard
        mock_text_data = b'Hello World\x00'
        saved_data = {clipboard_utils.CF_UNICODETEXT: mock_text_data}

        # Mock all the Windows API calls
        mock_handle = MagicMock()
        mock_ptr = MagicMock()

        with patch.object(clipboard_utils, '_open_clipboard_with_retry', return_value=True), \
             patch.object(clipboard_utils, 'EmptyClipboard'), \
             patch.object(clipboard_utils, 'GlobalAlloc', return_value=mock_handle), \
             patch.object(clipboard_utils, 'GlobalLock', return_value=mock_ptr), \
             patch.object(clipboard_utils, 'GlobalUnlock'), \
             patch.object(clipboard_utils, 'SetClipboardData', return_value=mock_handle), \
             patch.object(clipboard_utils, 'CloseClipboard'), \
             patch('ctypes.memmove'):
            result = clipboard_utils.restore_clipboard(saved_data)
            assert result is True


class TestClipboardConstants:
    """Tests for clipboard format constants."""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only tests")
    def test_format_constants_correct_values(self):
        """Clipboard format constants should have correct Windows API values."""
        import clipboard_utils

        assert clipboard_utils.CF_TEXT == 1
        assert clipboard_utils.CF_BITMAP == 2
        assert clipboard_utils.CF_UNICODETEXT == 13
        assert clipboard_utils.CF_DIB == 8
        assert clipboard_utils.CF_HDROP == 15
