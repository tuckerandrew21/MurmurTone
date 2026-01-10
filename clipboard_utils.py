"""
Clipboard save/restore utilities using Windows API via ctypes.

Allows saving clipboard contents before operations and restoring them afterwards,
preserving user's original clipboard data (screenshots, files, etc).
"""

import ctypes
import threading
import time
import logging
import sys
from ctypes import wintypes

log = logging.getLogger(__name__)

# Only available on Windows
if sys.platform != "win32":
    def save_clipboard():
        """No-op on non-Windows platforms."""
        return {}

    def restore_clipboard(saved):
        """No-op on non-Windows platforms."""
        pass

    def restore_clipboard_async(saved, delay_ms=400):
        """No-op on non-Windows platforms."""
        pass

else:
    # Windows API constants
    CF_TEXT = 1
    CF_BITMAP = 2
    CF_METAFILEPICT = 3
    CF_SYLK = 4
    CF_DIF = 5
    CF_TIFF = 6
    CF_OEMTEXT = 7
    CF_DIB = 8
    CF_PALETTE = 9
    CF_PENDATA = 10
    CF_RIFF = 11
    CF_WAVE = 12
    CF_UNICODETEXT = 13
    CF_ENHMETAFILE = 14
    CF_HDROP = 15
    CF_LOCALE = 16
    CF_DIBV5 = 17

    GMEM_MOVEABLE = 0x0002
    GMEM_ZEROINIT = 0x0040

    # Load Windows DLLs
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Clipboard functions
    OpenClipboard = user32.OpenClipboard
    OpenClipboard.argtypes = [wintypes.HWND]
    OpenClipboard.restype = wintypes.BOOL

    CloseClipboard = user32.CloseClipboard
    CloseClipboard.argtypes = []
    CloseClipboard.restype = wintypes.BOOL

    EmptyClipboard = user32.EmptyClipboard
    EmptyClipboard.argtypes = []
    EmptyClipboard.restype = wintypes.BOOL

    GetClipboardData = user32.GetClipboardData
    GetClipboardData.argtypes = [wintypes.UINT]
    GetClipboardData.restype = wintypes.HANDLE

    SetClipboardData = user32.SetClipboardData
    SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    SetClipboardData.restype = wintypes.HANDLE

    EnumClipboardFormats = user32.EnumClipboardFormats
    EnumClipboardFormats.argtypes = [wintypes.UINT]
    EnumClipboardFormats.restype = wintypes.UINT

    IsClipboardFormatAvailable = user32.IsClipboardFormatAvailable
    IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
    IsClipboardFormatAvailable.restype = wintypes.BOOL

    # Memory functions
    GlobalAlloc = kernel32.GlobalAlloc
    GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    GlobalAlloc.restype = wintypes.HGLOBAL

    GlobalLock = kernel32.GlobalLock
    GlobalLock.argtypes = [wintypes.HGLOBAL]
    GlobalLock.restype = wintypes.LPVOID

    GlobalUnlock = kernel32.GlobalUnlock
    GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    GlobalUnlock.restype = wintypes.BOOL

    GlobalSize = kernel32.GlobalSize
    GlobalSize.argtypes = [wintypes.HGLOBAL]
    GlobalSize.restype = ctypes.c_size_t

    GlobalFree = kernel32.GlobalFree
    GlobalFree.argtypes = [wintypes.HGLOBAL]
    GlobalFree.restype = wintypes.HGLOBAL

    # Formats we can reliably save/restore
    # Some formats like CF_BITMAP require special handling
    SUPPORTED_FORMATS = {
        CF_TEXT,
        CF_OEMTEXT,
        CF_UNICODETEXT,
        CF_DIB,
        CF_DIBV5,
        CF_HDROP,
        CF_LOCALE,
    }

    def _open_clipboard_with_retry(max_attempts=3, delay_ms=50):
        """Try to open clipboard with retries (it may be locked by another app)."""
        for attempt in range(max_attempts):
            if OpenClipboard(None):
                return True
            if attempt < max_attempts - 1:
                time.sleep(delay_ms / 1000.0)
        return False

    def save_clipboard() -> dict:
        """
        Save all supported clipboard formats.

        Returns:
            dict: Mapping of format_id -> bytes data. Empty dict if clipboard
                  is empty or couldn't be opened.
        """
        saved = {}

        if not _open_clipboard_with_retry():
            log.warning("Could not open clipboard to save contents")
            return saved

        try:
            # Enumerate all formats on clipboard
            fmt = 0
            while True:
                fmt = EnumClipboardFormats(fmt)
                if fmt == 0:
                    break

                # Only save formats we know how to restore
                if fmt not in SUPPORTED_FORMATS:
                    continue

                try:
                    handle = GetClipboardData(fmt)
                    if not handle:
                        continue

                    # Get data size
                    size = GlobalSize(handle)
                    if size == 0:
                        continue

                    # Lock memory and copy data
                    ptr = GlobalLock(handle)
                    if not ptr:
                        continue

                    try:
                        # Copy the data
                        data = ctypes.string_at(ptr, size)
                        saved[fmt] = data
                    finally:
                        GlobalUnlock(handle)

                except Exception as e:
                    log.debug(f"Could not save clipboard format {fmt}: {e}")
                    continue

        except Exception as e:
            log.warning(f"Error saving clipboard: {e}")
        finally:
            CloseClipboard()

        if saved:
            log.debug(f"Saved {len(saved)} clipboard format(s)")

        return saved

    def restore_clipboard(saved: dict) -> bool:
        """
        Restore previously saved clipboard contents.

        Args:
            saved: Dict from save_clipboard()

        Returns:
            bool: True if restore succeeded, False otherwise
        """
        if not saved:
            return True  # Nothing to restore

        if not _open_clipboard_with_retry():
            log.warning("Could not open clipboard to restore contents")
            return False

        try:
            EmptyClipboard()

            for fmt, data in saved.items():
                try:
                    # Allocate global memory
                    size = len(data)
                    handle = GlobalAlloc(GMEM_MOVEABLE, size)
                    if not handle:
                        log.debug(f"Could not allocate memory for format {fmt}")
                        continue

                    # Lock and copy data
                    ptr = GlobalLock(handle)
                    if not ptr:
                        GlobalFree(handle)
                        continue

                    try:
                        ctypes.memmove(ptr, data, size)
                    finally:
                        GlobalUnlock(handle)

                    # Set clipboard data (clipboard takes ownership of handle)
                    if not SetClipboardData(fmt, handle):
                        GlobalFree(handle)
                        log.debug(f"Could not set clipboard format {fmt}")

                except Exception as e:
                    log.debug(f"Could not restore clipboard format {fmt}: {e}")
                    continue

            log.debug(f"Restored {len(saved)} clipboard format(s)")
            return True

        except Exception as e:
            log.warning(f"Error restoring clipboard: {e}")
            return False
        finally:
            CloseClipboard()

    def restore_clipboard_async(saved: dict, delay_ms: int = 400) -> None:
        """
        Restore clipboard contents after a delay, in a background thread.

        This allows the paste operation to complete before we restore the
        original clipboard contents.

        Args:
            saved: Dict from save_clipboard()
            delay_ms: Milliseconds to wait before restoring (default 400)
        """
        if not saved:
            return

        def _restore_after_delay():
            time.sleep(delay_ms / 1000.0)
            restore_clipboard(saved)

        thread = threading.Thread(target=_restore_after_delay, daemon=True)
        thread.start()
