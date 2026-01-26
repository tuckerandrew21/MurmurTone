/**
 * MurmurTone Settings - JavaScript Controller
 * Handles tab switching, API communication, and UI state
 */

// ============================================
// State Management
// ============================================

let currentPage = 'general';
let settings = {};
let saveTimeout = null;
let isDownloading = false;
let modelDownloadStatus = {}; // Cache: { modelName: boolean }

/**
 * Update Download button visibility based on model installation status
 */
function updateDownloadButtonVisibility(modelName) {
    const downloadBtn = document.getElementById('download-model-btn');
    if (!downloadBtn) return;

    const bundledModels = ['tiny', 'base'];
    const isInstalled = bundledModels.includes(modelName) || modelDownloadStatus[modelName];

    downloadBtn.style.display = isInstalled ? 'none' : '';
}

// ============================================
// Model Download Callbacks (called from Python)
// ============================================

window.onModelDownloadProgress = function(percent, status) {
    const progressRow = document.getElementById('download-progress-row');
    const progressBar = document.getElementById('download-progress');
    const progressText = document.getElementById('download-progress-text');
    const downloadBtn = document.getElementById('download-model-btn');

    if (progressRow) progressRow.classList.remove('hidden');
    if (progressBar) progressBar.style.width = `${percent}%`;
    if (progressText) progressText.textContent = status;
    if (downloadBtn) {
        downloadBtn.disabled = true;
        downloadBtn.classList.add('loading');
    }
};

window.onModelDownloadComplete = function(success) {
    isDownloading = false;
    const progressRow = document.getElementById('download-progress-row');
    const downloadBtn = document.getElementById('download-model-btn');

    if (downloadBtn) {
        downloadBtn.disabled = false;
        downloadBtn.classList.remove('loading');
    }

    if (success) {
        showToast('Model downloaded successfully!', 'success');
        // Update cache so button hides
        const modelSelect = document.getElementById('model-size');
        if (modelSelect) {
            modelDownloadStatus[modelSelect.value] = true;
            updateDownloadButtonVisibility(modelSelect.value);
        }
        // Hide progress after a delay
        setTimeout(() => {
            if (progressRow) progressRow.classList.add('hidden');
        }, 2000);
    }
};

window.onModelDownloadError = function(error) {
    isDownloading = false;
    const progressRow = document.getElementById('download-progress-row');
    const downloadBtn = document.getElementById('download-model-btn');

    if (progressRow) progressRow.classList.add('hidden');
    if (downloadBtn) {
        downloadBtn.disabled = false;
        downloadBtn.classList.remove('loading');
    }

    showToast(`Download failed: ${error}`, 'error');
};

// ============================================
// Microphone Test Callbacks (called from Python)
// ============================================

let isMicTesting = false;

window.onAudioLevel = function(db) {
    const fill = document.getElementById('audio-level-fill');

    if (fill) {
        // Map -60 to -20 dB to 0-100%
        const percent = Math.max(0, Math.min(100, ((db + 60) / 40) * 100));
        fill.style.width = `${percent}%`;
    }
};

/**
 * Update threshold handle position based on current value
 */
function updateThresholdHandle() {
    const threshold = document.getElementById('noise-gate-threshold');
    const handle = document.getElementById('threshold-handle');

    if (threshold && handle) {
        const thresholdDb = parseInt(threshold.value || -40);
        const percent = ((thresholdDb + 60) / 40) * 100;
        handle.style.left = `${percent}%`;
    }
}

/**
 * Setup draggable threshold handle
 */
function setupThresholdDrag() {
    const meter = document.getElementById('threshold-meter');
    const handle = document.getElementById('threshold-handle');
    const threshold = document.getElementById('noise-gate-threshold');
    const valueDisplay = document.getElementById('noise-gate-threshold-value');

    if (!meter || !handle || !threshold) return;

    let isDragging = false;

    function updateFromPosition(clientX) {
        const rect = meter.getBoundingClientRect();
        const x = clientX - rect.left;
        const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));

        // Convert percent to dB (-60 to -20 range)
        const db = Math.round(-60 + (percent / 100) * 40);

        // Update handle position
        handle.style.left = `${percent}%`;

        // Update hidden input and display
        threshold.value = db;
        if (valueDisplay) {
            valueDisplay.textContent = `${db} dB`;
        }

        // Save to config
        saveSetting('noise_gate_threshold_db', db);
    }

    handle.addEventListener('mousedown', (e) => {
        isDragging = true;
        handle.classList.add('dragging');
        e.preventDefault();
    });

    meter.addEventListener('mousedown', (e) => {
        isDragging = true;
        handle.classList.add('dragging');
        updateFromPosition(e.clientX);
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            updateFromPosition(e.clientX);
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            handle.classList.remove('dragging');
        }
    });

    // Initialize handle position
    updateThresholdHandle();
}

/**
 * Toggle microphone test on/off
 */
async function toggleMicTest() {
    const btn = document.getElementById('mic-test-btn');
    const fill = document.getElementById('audio-level-fill');

    if (isMicTesting) {
        // Stop test
        try {
            await pywebview.api.stop_microphone_test();
        } catch (e) {
            console.error('Error stopping mic test:', e);
        }
        isMicTesting = false;
        if (btn) {
            btn.textContent = 'Test';
            btn.classList.remove('testing');
        }
        if (fill) {
            fill.style.width = '0%';
        }
    } else {
        // Start test
        try {
            const result = await pywebview.api.start_microphone_test();
            if (result.success) {
                isMicTesting = true;
                if (btn) {
                    btn.textContent = 'Stop';
                    btn.classList.add('testing');
                }
            } else {
                showToast(`Microphone test failed: ${result.error}`, 'error');
            }
        } catch (e) {
            console.error('Error starting mic test:', e);
            showToast('Failed to start microphone test', 'error');
        }
    }
}

// ============================================
// Initialization
// ============================================

/**
 * Wait for pywebview API to be ready, then initialize
 */
function init() {
    // Check if running in pywebview or browser (for testing)
    if (typeof pywebview !== 'undefined') {
        window.addEventListener('pywebviewready', onApiReady);
    } else {
        // PyWebView may not have injected yet - wait up to 2 seconds before falling back to mock
        let attempts = 0;
        const maxAttempts = 20; // 20 * 100ms = 2 seconds
        const checkPyWebView = setInterval(() => {
            attempts++;
            if (typeof pywebview !== 'undefined') {
                clearInterval(checkPyWebView);
                window.addEventListener('pywebviewready', onApiReady);
                // If pywebviewready already fired, trigger manually
                if (pywebview.api) {
                    onApiReady();
                }
            } else if (attempts >= maxAttempts) {
                clearInterval(checkPyWebView);
                // Running in browser for testing - use mock API
                console.log('Running in browser mode with mock API');
                window.pywebview = createMockApi();
                onApiReady();
            }
        }, 100);
    }
}

/**
 * Called when pywebview API is ready
 */
async function onApiReady() {
    console.log('PyWebView API ready');

    // Load settings from Python
    await loadSettings();

    // Set up event listeners
    setupNavigation();
    setupFormListeners();
    setupKeyboardNavigation();

    // Restore last active tab
    restoreActiveTab();

    // Toast click-to-dismiss
    const toast = document.getElementById('toast');
    if (toast) {
        toast.addEventListener('click', hideToast);
        toast.style.cursor = 'pointer';
    }

    // Update version display
    updateVersionDisplay();

    // Check if should show welcome banner (first run)
    checkFirstRun();
}

// ============================================
// API Communication
// ============================================

/**
 * Load all settings from Python API
 */
async function loadSettings() {
    const contentBody = document.querySelector('.content-body');
    if (contentBody) contentBody.classList.add('loading');

    try {
        const result = await pywebview.api.get_all_settings();
        if (result.success) {
            settings = result.data;
            await populateForm();
        } else {
            showToast('Failed to load settings: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        showToast('Failed to load settings', 'error');
    } finally {
        if (contentBody) {
            contentBody.classList.remove('loading');
            contentBody.classList.add('loaded');
            // Remove loaded class after animation completes
            setTimeout(() => contentBody.classList.remove('loaded'), 300);
        }
    }
}

/**
 * Save a single setting to Python API
 */
async function saveSetting(key, value) {
    try {
        const result = await pywebview.api.save_setting(key, value);
        if (result.success) {
            // Update local state
            if (key.includes('.')) {
                const parts = key.split('.');
                let target = settings;
                for (let i = 0; i < parts.length - 1; i++) {
                    target = target[parts[i]];
                }
                target[parts[parts.length - 1]] = value;
            } else {
                settings[key] = value;
            }
            showSaveStatus();
        } else {
            showToast('Failed to save: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error saving setting:', error);
        showToast('Failed to save setting', 'error');
    }
}

/**
 * Update version display in sidebar
 */
async function updateVersionDisplay() {
    try {
        const result = await pywebview.api.get_version_info();
        if (result.success) {
            const versionText = document.getElementById('version-text');
            if (versionText) {
                versionText.textContent = `${result.data.app_name} v${result.data.version}`;
            }
        }
    } catch (error) {
        console.error('Error getting version:', error);
    }
}

// ============================================
// Navigation
// ============================================

/**
 * Set up sidebar navigation click handlers
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            navigateTo(page);
        });
    });
}

/**
 * Navigate to a specific page
 */
function navigateTo(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // Update page visibility
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });

    // Scroll content to top when switching tabs
    const contentBody = document.querySelector('.content-body');
    if (contentBody) {
        contentBody.scrollTop = 0;
    }

    // Update page title
    const titles = {
        general: 'General',
        audio: 'Audio',
        recognition: 'Recognition',
        text: 'Text',
        advanced: 'Advanced',
        about: 'About'
    };
    document.getElementById('page-title').textContent = titles[page] || page;

    currentPage = page;

    // Persist active tab
    try {
        localStorage.setItem('murmurtone_active_tab', page);
    } catch (e) {
        // localStorage may not be available
    }
}

/**
 * Restore active tab from localStorage
 */
function restoreActiveTab() {
    try {
        const savedTab = localStorage.getItem('murmurtone_active_tab');
        if (savedTab && ['general', 'audio', 'recognition', 'text', 'advanced', 'about'].includes(savedTab)) {
            navigateTo(savedTab);
        }
    } catch (e) {
        // localStorage may not be available
    }
}

// ============================================
// Form Handling
// ============================================

/**
 * Populate form fields with current settings
 */
async function populateForm() {
    // Hotkey combo
    setHotkeyDisplay('hotkey-capture', settings.hotkey ?? { ctrl: true, shift: true, alt: false, key: 'space' });

    // Recording mode
    setDropdown('recording-mode', settings.recording_mode ?? 'push_to_talk');

    // Language
    setDropdown('language', settings.language ?? 'en');

    // Start with Windows
    setCheckbox('start-with-windows', settings.start_with_windows ?? false);

    // Audio settings
    setDropdown('sample-rate', settings.sample_rate ?? 16000);
    setCheckbox('noise-gate-enabled', settings.noise_gate_enabled ?? true);
    setSlider('noise-gate-threshold', settings.noise_gate_threshold_db ?? -40, 'dB');
    // Handle both 0.0-1.0 (legacy) and 0-100 formats
    let volumePercent = settings.audio_feedback_volume ?? 50;
    if (volumePercent <= 1) volumePercent = Math.round(volumePercent * 100);
    setSlider('feedback-volume', volumePercent, '%');
    setCheckbox('audio-feedback-enabled', settings.audio_feedback ?? true);
    setCheckbox('sound-processing', settings.sound_processing ?? true);
    setCheckbox('sound-success', settings.sound_success ?? true);
    setCheckbox('sound-error', settings.sound_error ?? true);
    setCheckbox('sound-command', settings.sound_command ?? true);

    // Update conditional visibility
    updateNoiseGateVisibility();
    updateAudioFeedbackVisibility();

    // Setup draggable threshold handle
    setupThresholdDrag();

    // Load audio devices
    loadAudioDevices();

    // Load dropdown options from backend (async, with fallback to hardcoded)
    // loadLanguageOptions updates both language and translation-source-language dropdowns
    loadLanguageOptions().then(() => {
        setDropdown('language', settings.language ?? 'en');
        setDropdown('translation-source-language', settings.translation_source_language ?? 'auto');
    });
    loadProcessingModeOptions().then(() => {
        setDropdown('processing-mode', settings.processing_mode ?? 'auto');
    });

    // Recognition settings
    setDropdown('model-size', settings.model_size ?? 'tiny');
    setSlider('silence-duration', settings.silence_duration_sec ?? 2.0, 's');

    // Fetch model download status and update button visibility
    try {
        const modelResult = await pywebview.api.get_available_models();
        if (modelResult.success) {
            modelResult.data.forEach(model => {
                modelDownloadStatus[model.name] = model.is_downloaded;
            });
        }
    } catch (e) {
        console.warn('Could not fetch model status:', e);
    }
    updateDownloadButtonVisibility(settings.model_size ?? 'tiny');

    // Translation settings
    setCheckbox('translation-enabled', settings.translation_enabled ?? false);
    updateTranslationVisibility();

    // Load vocabulary list
    loadVocabularyList();

    // Update editor counts
    updateDictionaryCount();
    updateShortcutsCount();
    updateVocabularyCount();
    updateFillerCount();

    // Check GPU status
    checkGpuStatus();

    // Text settings
    setCheckbox('auto-paste', settings.auto_paste ?? true);
    setDropdown('paste-mode', settings.paste_mode ?? 'clipboard');
    updatePasteModeHelp();
    setCheckbox('voice-commands', settings.voice_commands_enabled ?? true);
    setCheckbox('scratch-that', settings.scratch_that_enabled ?? true);
    setCheckbox('filler-removal', settings.filler_removal_enabled ?? true);
    setCheckbox('filler-aggressive', settings.filler_removal_aggressive ?? false);

    // Update nested setting visibility
    updateVoiceCommandsVisibility();
    updateFillerRemovalVisibility();

    // Load filler list
    loadFillerList();

    // Advanced settings - AI Cleanup
    setCheckbox('ai-cleanup', settings.ai_cleanup_enabled ?? false);
    setInput('ollama-url', settings.ollama_url ?? 'http://localhost:11434');
    setDropdown('ollama-model', settings.ollama_model ?? 'llama3.2:3b');
    setDropdown('ai-cleanup-mode', settings.ai_cleanup_mode ?? 'grammar');
    setDropdown('ai-formality-level', settings.ai_formality_level ?? 'professional');

    // Advanced settings - Preview
    setCheckbox('preview-enabled', settings.preview_enabled ?? true);
    setDropdown('preview-position', settings.preview_position ?? 'bottom_right');
    setSlider('preview-auto-hide', settings.preview_auto_hide_delay ?? 2.0, 's');
    setDropdown('preview-theme', settings.preview_theme ?? 'dark');
    const fontSize = settings.preview_font_size ?? 11;
    setSlider('preview-font-size', fontSize);
    const fontSizeValue = document.getElementById('preview-font-size-value');
    if (fontSizeValue) {
        fontSizeValue.textContent = `${fontSize}pt`;
    }

    // Update visibility
    updateAiCleanupVisibility();
    updatePreviewVisibility();
    toggleFormalityRow();
    hideOllamaConfigRows();

    // About page
    setCheckbox('auto-update', settings.auto_update ?? false);
    loadAboutInfo();
    loadLicenseStatus();
}

/**
 * Set up change listeners on all form elements
 */
function setupFormListeners() {
    // Hotkey combo capture
    setupHotkeyComboCapture('hotkey-capture', (hotkey) => saveSetting('hotkey', hotkey));

    // Recording mode
    addDropdownListener('recording-mode', (value) => saveSetting('recording_mode', value));

    // Language
    addDropdownListener('language', (value) => saveSetting('language', value));

    // Start with Windows (vertical slice)
    addCheckboxListener('start-with-windows', (checked) => saveSetting('start_with_windows', checked));

    // Audio settings
    addDropdownListener('input-device', (value) => saveSetting('input_device', value || null));
    addDropdownListener('sample-rate', (value) => saveSetting('sample_rate', parseInt(value)));
    addCheckboxListener('noise-gate-enabled', (checked) => {
        saveSetting('noise_gate_enabled', checked);
        updateNoiseGateVisibility();
    });
    // noise-gate-threshold is now handled by setupThresholdDrag()
    // Save as 0-100 directly
    addSliderListener('feedback-volume', (value) => {
        saveSetting('audio_feedback_volume', parseInt(value));
    }, '%');
    addCheckboxListener('audio-feedback-enabled', (checked) => {
        saveSetting('audio_feedback', checked);
        updateAudioFeedbackVisibility();
    });
    addCheckboxListener('sound-processing', (checked) => saveSetting('sound_processing', checked));
    addCheckboxListener('sound-success', (checked) => saveSetting('sound_success', checked));
    addCheckboxListener('sound-error', (checked) => saveSetting('sound_error', checked));
    addCheckboxListener('sound-command', (checked) => saveSetting('sound_command', checked));

    // Microphone test button
    const micTestBtn = document.getElementById('mic-test-btn');
    if (micTestBtn) {
        micTestBtn.addEventListener('click', toggleMicTest);
    }

    // Threshold handle is initialized in setupThresholdDrag()

    // Refresh devices button
    const refreshBtn = document.getElementById('refresh-devices-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadAudioDevices);
    }

    // Recognition settings
    addDropdownListener('model-size', (value) => {
        saveSetting('model_size', value);
        updateDownloadButtonVisibility(value);
    });
    addDropdownListener('processing-mode', (value) => saveSetting('processing_mode', value));
    addSliderListener('silence-duration', (value) => saveSetting('silence_duration_sec', parseFloat(value)), 's');

    // Translation settings
    addCheckboxListener('translation-enabled', (checked) => {
        saveSetting('translation_enabled', checked);
        updateTranslationVisibility();
    });
    addDropdownListener('translation-source-language', (value) => saveSetting('translation_source_language', value));

    // Translation learn more link
    const translationLearnMore = document.getElementById('translation-learn-more');
    if (translationLearnMore) {
        translationLearnMore.addEventListener('click', (e) => {
            e.preventDefault();
            pywebview.api.open_url('https://murmurtone.com/docs/translation');
        });
    }

    // Noise gate learn more link
    const noiseGateLearnMore = document.getElementById('noise-gate-learn-more');
    if (noiseGateLearnMore) {
        noiseGateLearnMore.addEventListener('click', (e) => {
            e.preventDefault();
            pywebview.api.open_url('https://murmurtone.com/docs/noise-gate');
        });
    }

    // Model learn more link
    const modelLearnMore = document.getElementById('model-learn-more');
    if (modelLearnMore) {
        modelLearnMore.addEventListener('click', (e) => {
            e.preventDefault();
            pywebview.api.open_url('https://murmurtone.com/docs/model-guide');
        });
    }

    // Processing mode learn more link
    const processingModeLearnMore = document.getElementById('processing-mode-learn-more');
    if (processingModeLearnMore) {
        processingModeLearnMore.addEventListener('click', (e) => {
            e.preventDefault();
            pywebview.api.open_url('https://murmurtone.com/docs/processing-mode');
        });
    }

    // AI cleanup learn more link
    const aiCleanupLearnMore = document.getElementById('ai-cleanup-learn-more');
    if (aiCleanupLearnMore) {
        aiCleanupLearnMore.addEventListener('click', (e) => {
            e.preventDefault();
            pywebview.api.open_url('https://murmurtone.com/docs/ai-cleanup');
        });
    }

    // Vocabulary list
    const addVocabBtn = document.getElementById('add-vocabulary-btn');
    const vocabInput = document.getElementById('vocabulary-input');
    if (addVocabBtn && vocabInput) {
        addVocabBtn.addEventListener('click', () => addVocabularyWord(vocabInput.value));
        vocabInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addVocabularyWord(vocabInput.value);
        });
    }

    // Vocabulary search/filter
    const vocabSearch = document.getElementById('vocabulary-search');
    if (vocabSearch) {
        vocabSearch.addEventListener('input', () => {
            filterList('vocabulary-list', vocabSearch.value);
        });
    }

    // Download model button
    const downloadBtn = document.getElementById('download-model-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', async () => {
            if (isDownloading) {
                showToast('Download already in progress', 'info');
                return;
            }

            const modelSelect = document.getElementById('model-size');
            const modelName = modelSelect ? modelSelect.value : 'small';

            // Check if model is bundled (no download needed)
            const bundledModels = ['tiny', 'base'];
            if (bundledModels.includes(modelName)) {
                showToast('This model is already bundled with MurmurTone', 'info');
                return;
            }

            isDownloading = true;
            downloadBtn.classList.add('loading');
            downloadBtn.disabled = true;
            showToast(`Starting download of ${modelName} model...`, 'info');

            try {
                await pywebview.api.download_model(modelName);
            } catch (e) {
                window.onModelDownloadError(e.message || 'Unknown error');
            }
        });
    }

    // Text settings
    addCheckboxListener('auto-paste', (checked) => saveSetting('auto_paste', checked));
    addDropdownListener('paste-mode', (value) => {
        saveSetting('paste_mode', value);
        updatePasteModeHelp();
    });
    addCheckboxListener('voice-commands', (checked) => {
        saveSetting('voice_commands_enabled', checked);
        updateVoiceCommandsVisibility();
    });
    addCheckboxListener('scratch-that', (checked) => saveSetting('scratch_that_enabled', checked));
    addCheckboxListener('filler-removal', (checked) => {
        saveSetting('filler_removal_enabled', checked);
        updateFillerRemovalVisibility();
    });
    addCheckboxListener('filler-aggressive', (checked) => saveSetting('filler_removal_aggressive', checked));

    // Filler list
    const addFillerBtn = document.getElementById('add-filler-btn');
    const fillerInput = document.getElementById('filler-input');
    if (addFillerBtn && fillerInput) {
        addFillerBtn.addEventListener('click', () => addFillerWord(fillerInput.value));
        fillerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addFillerWord(fillerInput.value);
        });
    }

    // Filler search/filter
    const fillerSearch = document.getElementById('filler-search');
    if (fillerSearch) {
        fillerSearch.addEventListener('input', () => {
            filterList('filler-list', fillerSearch.value);
        });
    }

    // Advanced settings - AI Cleanup
    addCheckboxListener('ai-cleanup', (checked) => {
        saveSetting('ai_cleanup_enabled', checked);
        updateAiCleanupVisibility();

        // Auto-test Ollama connection when enabled
        if (checked) {
            setTimeout(() => testOllamaConnection(), 200);
        } else {
            // Hide action row when disabled
            const actionRow = document.getElementById('ollama-action-row');
            if (actionRow) actionRow.style.display = 'none';
        }
    });
    addInputListener('ollama-url', (value) => saveSetting('ollama_url', value), 1000);
    addDropdownListener('ollama-model', (value) => saveSetting('ollama_model', value));
    addDropdownListener('ai-cleanup-mode', (value) => {
        saveSetting('ai_cleanup_mode', value);
        toggleFormalityRow();
    });
    addDropdownListener('ai-formality-level', (value) => saveSetting('ai_formality_level', value));

    // Test Ollama connection button
    const testOllamaBtn = document.getElementById('test-ollama-btn');
    if (testOllamaBtn) {
        testOllamaBtn.addEventListener('click', testOllamaConnection);
    }

    // Retry Ollama connection button
    const retryOllamaBtn = document.getElementById('retry-ollama-btn');
    if (retryOllamaBtn) {
        retryOllamaBtn.addEventListener('click', testOllamaConnection);
    }

    // Download Ollama button
    const downloadOllamaBtn = document.getElementById('download-ollama-btn');
    if (downloadOllamaBtn) {
        downloadOllamaBtn.addEventListener('click', () => {
            window.open('https://ollama.ai/download', '_blank');
        });
    }

    // Show Ollama config button
    const showOllamaConfigBtn = document.getElementById('show-ollama-config-btn');
    if (showOllamaConfigBtn) {
        showOllamaConfigBtn.addEventListener('click', () => {
            showOllamaConfigRows();
            // Auto-scroll to the URL input
            const urlRow = document.getElementById('ollama-url-row');
            if (urlRow) {
                urlRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }

    // Advanced settings - Preview
    addCheckboxListener('preview-enabled', (checked) => {
        saveSetting('preview_enabled', checked);
        updatePreviewVisibility();
    });
    addDropdownListener('preview-position', (value) => saveSetting('preview_position', value));
    addSliderListener('preview-auto-hide', (value) => saveSetting('preview_auto_hide_delay', parseFloat(value)), 's');
    addDropdownListener('preview-theme', (value) => saveSetting('preview_theme', value));
    addSliderListener('preview-font-size', (value) => {
        saveSetting('preview_font_size', parseInt(value));
        const valueDisplay = document.getElementById('preview-font-size-value');
        if (valueDisplay) {
            valueDisplay.textContent = `${value}pt`;
        }
    });

    // Install GPU Support button
    const installGpuBtn = document.getElementById('install-gpu-btn');
    if (installGpuBtn) {
        installGpuBtn.addEventListener('click', installGpuSupport);
    }

    // Refresh GPU Status button
    const refreshGpuBtn = document.getElementById('refresh-gpu-btn');
    if (refreshGpuBtn) {
        refreshGpuBtn.addEventListener('click', refreshGpuStatus);
    }

    // Reset to defaults button
    const resetBtn = document.getElementById('reset-defaults-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', confirmResetDefaults);
    }

    // Modal editors
    setupDictionaryModal();
    setupShortcutsModal();
    setupVocabularyModal();
    setupFillersModal();
    setupHistoryModal();

    // About page - Auto update toggle
    addCheckboxListener('auto-update', (checked) => saveSetting('auto_update', checked));

    // About page - Check for updates button
    const checkUpdatesBtn = document.getElementById('check-updates-btn');
    console.log('Check updates button element:', checkUpdatesBtn);
    if (checkUpdatesBtn) {
        checkUpdatesBtn.addEventListener('click', async () => {
            console.log('Check updates button clicked');
            checkUpdatesBtn.disabled = true;
            checkUpdatesBtn.textContent = 'Checking...';
            try {
                console.log('Calling pywebview.api.check_for_updates()...');
                const result = await pywebview.api.check_for_updates();
                console.log('Update check result:', result);
                if (result.success && result.data.update_available) {
                    console.log('Update available, showing modal');
                    // Show branded modal instead of toast
                    showUpdateModal(result.data);
                } else if (result.success) {
                    console.log('No update available, showing success toast');
                    showToast('You have the latest version', 'success');
                } else {
                    console.log('Update check unsuccessful, showing error toast');
                    showToast('Could not check for updates', 'error');
                }
            } catch (error) {
                console.error('Update check error:', error);
                showToast('Update check failed', 'error');
            } finally {
                console.log('Resetting button state');
                checkUpdatesBtn.disabled = false;
                setTimeout(() => {
                    checkUpdatesBtn.textContent = 'Check Now';
                }, 3000);
            }
        });
    }

    // About page - License activation
    const activateBtn = document.getElementById('activate-license-btn');
    const licenseInput = document.getElementById('license-key');
    if (activateBtn && licenseInput) {
        activateBtn.addEventListener('click', () => activateLicense(licenseInput.value));
        licenseInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') activateLicense(licenseInput.value);
        });
    }

    // Purchase button
    const purchaseBtn = document.getElementById('purchase-btn');
    if (purchaseBtn) {
        purchaseBtn.addEventListener('click', () => {
            pywebview.api.open_url('https://murmurtone.com/purchase');
        });
    }

    // Link buttons (Documentation, Support, Visit Website)
    document.querySelectorAll('.link-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const url = btn.dataset.url;
            if (url) pywebview.api.open_url(url);
        });
    });

    // Open Logs Folder button
    const openLogsBtn = document.getElementById('open-logs-btn');
    if (openLogsBtn) {
        openLogsBtn.addEventListener('click', async () => {
            try {
                await pywebview.api.open_logs_folder();
            } catch (error) {
                console.error('Failed to open logs folder:', error);
                showToast('Failed to open logs folder', 'error');
            }
        });
    }
}

// ============================================
// Form Helpers
// ============================================

function setCheckbox(id, checked) {
    const el = document.getElementById(id);
    if (el) el.checked = checked;
}

function setDropdown(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value;
}

function setInput(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value;
}

function addCheckboxListener(id, callback) {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('change', () => callback(el.checked));
    }
}

function addDropdownListener(id, callback) {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('change', () => callback(el.value));
    }
}

/**
 * Format a hotkey object for display (e.g., { ctrl: true, shift: true, key: 'space' } -> 'Ctrl + Shift + Space')
 */
function formatHotkeyCombo(hotkey) {
    if (!hotkey || !hotkey.key) return 'Not set';
    const parts = [];
    if (hotkey.ctrl) parts.push('Ctrl');
    if (hotkey.shift) parts.push('Shift');
    if (hotkey.alt) parts.push('Alt');
    // Format the key
    let keyDisplay = hotkey.key;
    if (keyDisplay === 'space' || keyDisplay === ' ') keyDisplay = 'Space';
    else if (keyDisplay.match(/^f\d+$/i)) keyDisplay = keyDisplay.toUpperCase();
    else keyDisplay = keyDisplay.charAt(0).toUpperCase() + keyDisplay.slice(1);
    parts.push(keyDisplay);
    return parts.join(' + ');
}

/**
 * Set the displayed value of the hotkey capture button
 */
function setHotkeyDisplay(id, hotkey) {
    const btn = document.getElementById(id);
    if (btn) {
        const display = btn.querySelector('.hotkey-display');
        if (display) {
            display.textContent = formatHotkeyCombo(hotkey);
        }
        btn.dataset.hotkey = JSON.stringify(hotkey);
    }
}

/**
 * Set up hotkey combo capture - captures full key combination (e.g., Ctrl+Shift+X)
 */
function setupHotkeyComboCapture(id, callback) {
    const btn = document.getElementById(id);
    if (!btn) return;

    btn.addEventListener('click', () => {
        // Already capturing, ignore
        if (btn.classList.contains('capturing')) return;

        const currentHotkey = JSON.parse(btn.dataset.hotkey || '{"ctrl":true,"shift":true,"alt":false,"key":"space"}');
        btn.classList.add('capturing');
        const display = btn.querySelector('.hotkey-display');
        if (display) {
            display.textContent = 'Press key combo...';
        }

        const handleKey = (e) => {
            e.preventDefault();
            e.stopPropagation();

            // Ignore modifier-only presses - wait for a real key
            if (['Control', 'Shift', 'Alt', 'Meta'].includes(e.key)) {
                return;
            }

            document.removeEventListener('keydown', handleKey);
            btn.classList.remove('capturing');

            // Escape cancels
            if (e.key === 'Escape') {
                setHotkeyDisplay(id, currentHotkey);
                return;
            }

            // Build the hotkey from current modifiers + key
            const newHotkey = {
                ctrl: e.ctrlKey,
                shift: e.shiftKey,
                alt: e.altKey,
                key: e.key === ' ' ? 'space' : e.key.toLowerCase()
            };

            setHotkeyDisplay(id, newHotkey);
            callback(newHotkey);
        };

        document.addEventListener('keydown', handleKey);
    });
}

function addInputListener(id, callback, debounce = 500) {
    const el = document.getElementById(id);
    if (el) {
        let timeout;
        el.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => callback(el.value), debounce);
        });
    }
}

function setSlider(id, value, unit = '') {
    const el = document.getElementById(id);
    const valueEl = document.getElementById(`${id}-value`);
    if (el) {
        el.value = value;
        updateSliderFill(el);
        if (valueEl) {
            valueEl.textContent = `${value}${unit ? ' ' + unit : ''}`;
        }
    }
}

function addSliderListener(id, callback, unit = '') {
    const el = document.getElementById(id);
    const valueEl = document.getElementById(`${id}-value`);
    if (el) {
        el.addEventListener('input', () => {
            updateSliderFill(el);
            if (valueEl) {
                valueEl.textContent = `${el.value}${unit ? ' ' + unit : ''}`;
            }
        });
        el.addEventListener('change', () => callback(el.value));
    }
}

/**
 * Update slider track fill based on current value
 */
function updateSliderFill(slider) {
    const min = parseFloat(slider.min) || 0;
    const max = parseFloat(slider.max) || 100;
    const value = parseFloat(slider.value) || 0;
    const percentage = ((value - min) / (max - min)) * 100;
    slider.style.setProperty('--slider-fill', `${percentage}%`);
}

// ============================================
// Audio Device Management
// ============================================

/**
 * Load audio devices into the dropdown
 */
async function loadAudioDevices() {
    const dropdown = document.getElementById('input-device');
    const refreshBtn = document.getElementById('refresh-devices-btn');

    if (!dropdown) return;

    // Show loading state
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.classList.add('loading');
    }

    try {
        const result = await pywebview.api.get_audio_devices();
        if (result.success) {
            // Find the system default entry (has id: null)
            // Python backend already formats it as "System Default (device name)"
            const defaultEntry = result.data.find(d => !d.id);
            const defaultLabel = defaultEntry?.name || 'System Default';

            // Clear existing options and add default
            dropdown.innerHTML = `<option value="">${defaultLabel}</option>`;

            // Add devices
            result.data.forEach(device => {
                if (device.id) {  // Skip the default entry
                    const option = document.createElement('option');
                    option.value = device.id;
                    option.textContent = device.name;
                    dropdown.appendChild(option);
                }
            });

            // Select current device
            if (settings.input_device) {
                dropdown.value = settings.input_device;
            }
        } else {
            showToast('Failed to load audio devices: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error loading audio devices:', error);
        showToast('Failed to load audio devices', 'error');
    } finally {
        // Remove loading state
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.classList.remove('loading');
        }
    }
}

/**
 * Load language options from backend
 */
async function loadLanguageOptions() {
    const languageDropdown = document.getElementById('language');
    const translationDropdown = document.getElementById('translation-source-language');

    try {
        const result = await pywebview.api.get_language_options();
        if (result.success && result.data) {
            const currentLanguage = languageDropdown?.value;
            const currentTranslation = translationDropdown?.value;

            // Update language dropdown
            if (languageDropdown) {
                languageDropdown.innerHTML = '';
                result.data.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.code;
                    option.textContent = opt.label;
                    languageDropdown.appendChild(option);
                });
                if (currentLanguage) languageDropdown.value = currentLanguage;
            }

            // Update translation source dropdown (same options)
            if (translationDropdown) {
                translationDropdown.innerHTML = '';
                result.data.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.code;
                    option.textContent = opt.label;
                    translationDropdown.appendChild(option);
                });
                if (currentTranslation) translationDropdown.value = currentTranslation;
            }
        }
    } catch (error) {
        console.error('Error loading language options:', error);
        // Keep existing hardcoded options as fallback
    }
}

/**
 * Load processing mode options from backend
 */
async function loadProcessingModeOptions() {
    const dropdown = document.getElementById('processing-mode');
    if (!dropdown) return;

    try {
        const result = await pywebview.api.get_processing_mode_options();
        if (result.success && result.data) {
            const currentValue = dropdown.value;

            dropdown.innerHTML = '';
            result.data.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt.code;
                option.textContent = opt.label;
                if (opt.code === 'auto') {
                    option.textContent += ' (Recommended)';
                }
                dropdown.appendChild(option);
            });

            if (currentValue) dropdown.value = currentValue;
        }
    } catch (error) {
        console.error('Error loading processing mode options:', error);
        // Keep existing hardcoded options as fallback
    }
}

/**
 * Update noise gate options visibility based on toggle state
 */
function updateNoiseGateVisibility() {
    const enabled = document.getElementById('noise-gate-enabled')?.checked;
    const options = document.getElementById('noise-gate-options');

    if (options) {
        if (enabled) {
            options.classList.remove('hidden');
        } else {
            options.classList.add('hidden');
        }
    }
}

/**
 * Update audio feedback sub-options visibility based on master toggle
 */
function updateAudioFeedbackVisibility() {
    const enabled = document.getElementById('audio-feedback-enabled')?.checked;
    const options = document.getElementById('audio-feedback-options');

    if (options) {
        if (enabled) {
            options.classList.remove('disabled');
        } else {
            options.classList.add('disabled');
        }
    }
}

// ============================================
// Vocabulary List Management
// ============================================

/**
 * Load vocabulary list from settings
 */
function loadVocabularyList() {
    const list = document.getElementById('vocabulary-list');
    const emptyState = document.getElementById('vocabulary-empty');
    if (!list) return;

    const words = settings.custom_vocabulary || [];

    list.innerHTML = '';

    if (words.length === 0) {
        if (emptyState) emptyState.classList.remove('hidden');
    } else {
        if (emptyState) emptyState.classList.add('hidden');
        words.forEach(word => {
            const item = createListItem(word, () => removeVocabularyWord(word));
            list.appendChild(item);
        });
    }
}

/**
 * Add a word to the vocabulary list
 */
async function addVocabularyWord(word) {
    word = word.trim();
    if (!word) return;

    const words = settings.custom_vocabulary || [];
    if (words.includes(word)) {
        showToast('Word already in vocabulary', 'info');
        return;
    }

    words.push(word);
    const result = await saveSetting('custom_vocabulary', words);

    if (result) {
        settings.custom_vocabulary = words;
        loadVocabularyList();

        // Clear input
        const input = document.getElementById('vocabulary-input');
        if (input) input.value = '';
    }
}

/**
 * Remove a word from the vocabulary list
 */
async function removeVocabularyWord(word) {
    const words = settings.custom_vocabulary || [];
    const index = words.indexOf(word);
    if (index === -1) return;

    words.splice(index, 1);
    const result = await saveSetting('custom_vocabulary', words);

    if (result) {
        settings.custom_vocabulary = words;
        loadVocabularyList();
    }
}

/**
 * Create a list item element with delete button
 */
function createListItem(text, onDelete) {
    const li = document.createElement('li');
    li.className = 'editable-list-item';

    const span = document.createElement('span');
    span.className = 'item-text';
    span.textContent = text;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'delete-btn';
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    btn.addEventListener('click', onDelete);

    li.appendChild(span);
    li.appendChild(btn);
    return li;
}

/**
 * Filter list items by search term
 */
function filterList(listId, searchTerm) {
    const list = document.getElementById(listId);
    if (!list) return;

    const term = searchTerm.toLowerCase().trim();
    const items = list.querySelectorAll('.editable-list-item');
    let visibleCount = 0;

    items.forEach(item => {
        const text = item.querySelector('.item-text')?.textContent.toLowerCase() || '';
        if (!term || text.includes(term)) {
            item.classList.remove('filtered');
            visibleCount++;
        } else {
            item.classList.add('filtered');
        }
    });

    // Update empty state visibility
    const emptyId = listId.replace('-list', '-empty');
    const emptyState = document.getElementById(emptyId);
    if (emptyState) {
        if (visibleCount === 0 && items.length > 0) {
            emptyState.textContent = 'No matches found.';
            emptyState.classList.remove('hidden');
        } else if (items.length === 0) {
            emptyState.textContent = listId === 'vocabulary-list' ?
                'No custom vocabulary added yet.' : 'No custom filler words added.';
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
        }
    }
}

// ============================================
// GPU Status
// ============================================

/**
 * Check GPU availability and update status badge
 */
async function checkGpuStatus() {
    const badge = document.getElementById('gpu-status');
    const installRow = document.getElementById('install-gpu-row');
    if (!badge) return;

    badge.className = 'status-badge checking';
    badge.querySelector('.status-text').textContent = 'Checking GPU...';

    try {
        const result = await pywebview.api.get_gpu_status();
        if (result.success && result.data.available) {
            badge.className = 'status-badge available';
            badge.querySelector('.status-text').textContent =
                `GPU Available: ${result.data.name || 'GPU'}`;
            // Hide install button when GPU is available
            if (installRow) installRow.classList.add('hidden');
        } else {
            badge.className = 'status-badge unavailable';
            badge.querySelector('.status-text').textContent = 'GPU Not Available';
            // Show install button when GPU is not available
            if (installRow) installRow.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error checking GPU:', error);
        badge.className = 'status-badge unavailable';
        badge.querySelector('.status-text').textContent = 'GPU Status Unknown';
        // Show install button on error
        if (installRow) installRow.classList.remove('hidden');
    }
}

/**
 * Refresh GPU status with user feedback
 */
async function refreshGpuStatus() {
    const btn = document.getElementById('refresh-gpu-btn');
    if (!btn) return;

    const icon = btn.querySelector('.refresh-icon');
    btn.disabled = true;
    if (icon) icon.classList.add('spinning');

    try {
        await checkGpuStatus();
        showToast('GPU status refreshed', 'success');
    } catch (error) {
        console.error('Error refreshing GPU:', error);
        showToast('Failed to refresh GPU status', 'error');
    } finally {
        btn.disabled = false;
        if (icon) icon.classList.remove('spinning');
    }
}

/**
 * Install GPU support libraries
 */
async function installGpuSupport() {
    const btn = document.getElementById('install-gpu-btn');
    if (!btn) return;

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Installing...';

    try {
        const result = await pywebview.api.install_gpu_support();
        if (result.success) {
            showToast('GPU support installed! Please restart the application.', 'success');
            // Recheck GPU status
            await checkGpuStatus();
        } else {
            showToast(result.message || 'Failed to install GPU support', 'error');
        }
    } catch (error) {
        console.error('Error installing GPU support:', error);
        showToast('Failed to install GPU support. See manual instructions.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// ============================================
// Filler List Management
// ============================================

/**
 * Load filler list from settings
 */
function loadFillerList() {
    const list = document.getElementById('filler-list');
    const emptyState = document.getElementById('filler-empty');
    if (!list) return;

    const words = settings.custom_fillers || [];

    list.innerHTML = '';

    if (words.length === 0) {
        if (emptyState) emptyState.classList.remove('hidden');
    } else {
        if (emptyState) emptyState.classList.add('hidden');
        words.forEach(word => {
            const item = createListItem(word, () => removeFillerWord(word));
            list.appendChild(item);
        });
    }
}

/**
 * Add a word to the filler list
 */
async function addFillerWord(word) {
    word = word.trim().toLowerCase();
    if (!word) return;

    const words = settings.custom_fillers || [];
    if (words.includes(word)) {
        showToast('Word already in list', 'info');
        return;
    }

    words.push(word);
    const result = await saveSetting('custom_fillers', words);

    if (result) {
        settings.custom_fillers = words;
        loadFillerList();

        // Clear input
        const input = document.getElementById('filler-input');
        if (input) input.value = '';
    }
}

/**
 * Remove a word from the filler list
 */
async function removeFillerWord(word) {
    const words = settings.custom_fillers || [];
    const index = words.indexOf(word);
    if (index === -1) return;

    words.splice(index, 1);
    const result = await saveSetting('custom_fillers', words);

    if (result) {
        settings.custom_fillers = words;
        loadFillerList();
    }
}

// ============================================
// Nested Setting Visibility
// ============================================

/**
 * Update voice commands sub-options visibility
 */
function updateVoiceCommandsVisibility() {
    const enabled = document.getElementById('voice-commands')?.checked;
    const scratchRow = document.getElementById('scratch-that-row');

    if (scratchRow) {
        if (enabled) {
            scratchRow.classList.remove('disabled');
        } else {
            scratchRow.classList.add('disabled');
        }
    }
}

/**
 * Update filler removal sub-options visibility
 */
function updateFillerRemovalVisibility() {
    const enabled = document.getElementById('filler-removal')?.checked;
    const aggressiveRow = document.getElementById('filler-aggressive-row');
    const customSection = document.getElementById('custom-fillers-section');

    [aggressiveRow, customSection].forEach(el => {
        if (el) {
            if (enabled) {
                el.classList.remove('disabled');
            } else {
                el.classList.add('disabled');
            }
        }
    });
}

/**
 * Update translation sub-options visibility
 */
function updateTranslationVisibility() {
    const enabled = document.getElementById('translation-enabled')?.checked;
    const languageRow = document.getElementById('translation-language-row');

    if (languageRow) {
        if (enabled) {
            languageRow.classList.remove('disabled');
        } else {
            languageRow.classList.add('disabled');
        }
    }
}

/**
 * Update AI cleanup sub-options visibility
 */
function updateAiCleanupVisibility() {
    const enabled = document.getElementById('ai-cleanup')?.checked;
    const options = document.getElementById('ai-cleanup-options');

    if (options) {
        if (enabled) {
            options.classList.remove('disabled');
        } else {
            options.classList.add('disabled');
        }
    }
}

/**
 * Toggle formality row visibility based on cleanup mode
 * Hide when mode is 'grammar' (grammar-only doesn't need formality level)
 */
function toggleFormalityRow() {
    const mode = document.getElementById('ai-cleanup-mode')?.value;
    const formalityRow = document.getElementById('formality-row');

    if (formalityRow) {
        // Show formality row for 'formality' and 'both' modes, hide for 'grammar'
        formalityRow.style.display = (mode === 'grammar') ? 'none' : 'flex';
    }
}

/**
 * Hide Ollama configuration rows (URL, status, model)
 * These are technical settings that most users don't need to see
 */
function hideOllamaConfigRows() {
    const urlRow = document.getElementById('ollama-url-row');
    const statusRow = document.getElementById('ollama-status-row');
    const modelRow = document.getElementById('ollama-model-row');
    const actionRow = document.getElementById('ollama-action-row');

    if (urlRow) urlRow.style.display = 'none';
    if (statusRow) statusRow.style.display = 'none';
    if (modelRow) modelRow.style.display = 'none';
    if (actionRow) actionRow.style.display = 'none';
}

/**
 * Show Ollama configuration rows (for troubleshooting)
 */
function showOllamaConfigRows() {
    const urlRow = document.getElementById('ollama-url-row');
    const statusRow = document.getElementById('ollama-status-row');
    const modelRow = document.getElementById('ollama-model-row');
    const actionRow = document.getElementById('ollama-action-row');

    if (urlRow) urlRow.style.display = 'flex';
    if (statusRow) statusRow.style.display = 'flex';
    if (modelRow) modelRow.style.display = 'flex';
    if (actionRow) actionRow.style.display = 'none'; // Hide action row when showing config
}

/**
 * Update preview sub-options visibility
 */
function updatePreviewVisibility() {
    const enabled = document.getElementById('preview-enabled')?.checked;
    const options = document.getElementById('preview-options');

    if (options) {
        if (enabled) {
            options.classList.remove('disabled');
        } else {
            options.classList.add('disabled');
        }
    }
}

/**
 * Update paste mode help text based on selected mode
 */
function updatePasteModeHelp() {
    const mode = document.getElementById('paste-mode')?.value;
    const helpText = document.getElementById('paste-mode-help');
    if (!helpText) return;

    const helpTexts = {
        'clipboard': 'Copies text to clipboard and pastes with Ctrl+V',
        'direct': 'Simulates typing each character (slower but more compatible)'
    };

    helpText.textContent = helpTexts[mode] || 'How text is inserted';
}

// ============================================
// Modal Dialogs
// ============================================

let dictionaryData = [];
let shortcutsData = [];

/**
 * Open a modal dialog
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Close a modal dialog
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('visible');
        document.body.style.overflow = '';
    }
}

/**
 * Show update available modal
 */
function showUpdateModal(updateData) {
    const modal = document.getElementById('update-modal');
    const versionEl = document.getElementById('update-version-number');
    const currentEl = document.getElementById('current-version-number');
    const downloadBtn = document.getElementById('update-download-btn');
    const laterBtn = document.getElementById('update-later-btn');
    const closeBtn = document.getElementById('update-modal-close');

    if (!modal || !versionEl || !currentEl) return;

    // Populate version numbers
    versionEl.textContent = updateData.latest_version;
    currentEl.textContent = updateData.current_version;

    // Show modal
    modal.classList.add('visible');
    document.body.style.overflow = 'hidden';

    // Handle download button
    const handleDownload = () => {
        if (updateData.download_url) {
            pywebview.api.open_url(updateData.download_url);
        }
        modal.classList.remove('visible');
        document.body.style.overflow = '';
        cleanup();
    };

    // Handle later button and close
    const handleClose = () => {
        modal.classList.remove('visible');
        document.body.style.overflow = '';
        cleanup();
    };

    const cleanup = () => {
        downloadBtn.removeEventListener('click', handleDownload);
        laterBtn.removeEventListener('click', handleClose);
        closeBtn.removeEventListener('click', handleClose);
    };

    // Attach event listeners
    downloadBtn.addEventListener('click', handleDownload);
    laterBtn.addEventListener('click', handleClose);
    closeBtn.addEventListener('click', handleClose);
}

// Expose to Python backend
if (typeof window !== 'undefined') {
    window.showUpdateModal = showUpdateModal;
}

/**
 * Setup dictionary editor modal
 */
function setupDictionaryModal() {
    const editBtn = document.getElementById('edit-dictionary-btn');
    const modal = document.getElementById('dictionary-modal');
    const closeBtn = document.getElementById('dictionary-modal-close');
    const cancelBtn = document.getElementById('dictionary-cancel');
    const saveBtn = document.getElementById('dictionary-save');
    const addRowBtn = document.getElementById('add-dictionary-row');

    if (editBtn) {
        editBtn.addEventListener('click', () => {
            dictionaryData = [...(settings.custom_dictionary || [])];
            renderDictionaryTable();
            openModal('dictionary-modal');
        });
    }

    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('dictionary-modal'));
    if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('dictionary-modal'));

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            // Collect data from table
            const rows = document.querySelectorAll('#dictionary-tbody tr');
            const newData = [];
            rows.forEach(row => {
                const inputs = row.querySelectorAll('input');
                const from = inputs[0]?.value.trim();
                const to = inputs[1]?.value.trim();
                if (from && to) {
                    newData.push({ from, to });
                }
            });
            settings.custom_dictionary = newData;
            saveSetting('custom_dictionary', newData);
            updateDictionaryCount();
            closeModal('dictionary-modal');
            showToast('Dictionary saved', 'success');
        });
    }

    if (addRowBtn) {
        addRowBtn.addEventListener('click', () => {
            dictionaryData.push({ from: '', to: '' });
            renderDictionaryTable();
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal('dictionary-modal');
        });
    }
}

/**
 * Render the dictionary table rows
 */
function renderDictionaryTable() {
    const tbody = document.getElementById('dictionary-tbody');
    if (!tbody) return;

    tbody.innerHTML = '';
    dictionaryData.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="text" value="${escapeHtml(item.from || '')}" placeholder="Original word"></td>
            <td><input type="text" value="${escapeHtml(item.to || '')}" placeholder="Replacement"></td>
            <td>
                <button type="button" class="delete-row-btn" data-index="${index}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </td>
        `;
        tbody.appendChild(row);

        // Add delete handler
        row.querySelector('.delete-row-btn').addEventListener('click', () => {
            dictionaryData.splice(index, 1);
            renderDictionaryTable();
        });
    });

    // Add empty row if no data
    if (dictionaryData.length === 0) {
        dictionaryData.push({ from: '', to: '' });
        renderDictionaryTable();
    }
}

/**
 * Update dictionary count display
 */
function updateDictionaryCount() {
    const countEl = document.getElementById('dictionary-count');
    const count = (settings.custom_dictionary || []).filter(d => d.from && d.to).length;
    if (countEl) {
        countEl.textContent = `${count} replacement${count !== 1 ? 's' : ''} defined`;
    }
}

/**
 * Setup shortcuts editor modal
 */
function setupShortcutsModal() {
    const editBtn = document.getElementById('edit-shortcuts-btn');
    const modal = document.getElementById('shortcuts-modal');
    const closeBtn = document.getElementById('shortcuts-modal-close');
    const cancelBtn = document.getElementById('shortcuts-cancel');
    const saveBtn = document.getElementById('shortcuts-save');
    const addRowBtn = document.getElementById('add-shortcuts-row');

    if (editBtn) {
        editBtn.addEventListener('click', () => {
            shortcutsData = [...(settings.custom_commands || [])];
            renderShortcutsTable();
            openModal('shortcuts-modal');
        });
    }

    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('shortcuts-modal'));
    if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('shortcuts-modal'));

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            // Collect data from table
            const rows = document.querySelectorAll('#shortcuts-tbody tr');
            const newData = [];
            rows.forEach(row => {
                const inputs = row.querySelectorAll('input');
                const trigger = inputs[0]?.value.trim();
                const replacement = inputs[1]?.value.trim();
                if (trigger && replacement) {
                    newData.push({ trigger, replacement });
                }
            });
            settings.custom_commands = newData;
            saveSetting('custom_commands', newData);
            updateShortcutsCount();
            closeModal('shortcuts-modal');
            showToast('Shortcuts saved', 'success');
        });
    }

    if (addRowBtn) {
        addRowBtn.addEventListener('click', () => {
            shortcutsData.push({ trigger: '', replacement: '' });
            renderShortcutsTable();
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal('shortcuts-modal');
        });
    }
}

/**
 * Render the shortcuts table rows
 */
function renderShortcutsTable() {
    const tbody = document.getElementById('shortcuts-tbody');
    if (!tbody) return;

    tbody.innerHTML = '';
    shortcutsData.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="text" value="${escapeHtml(item.trigger || '')}" placeholder="Trigger phrase"></td>
            <td><input type="text" value="${escapeHtml(item.replacement || '')}" placeholder="Expansion text"></td>
            <td>
                <button type="button" class="delete-row-btn" data-index="${index}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </td>
        `;
        tbody.appendChild(row);

        // Add delete handler
        row.querySelector('.delete-row-btn').addEventListener('click', () => {
            shortcutsData.splice(index, 1);
            renderShortcutsTable();
        });
    });

    // Add empty row if no data
    if (shortcutsData.length === 0) {
        shortcutsData.push({ trigger: '', replacement: '' });
        renderShortcutsTable();
    }
}

/**
 * Update shortcuts count display
 */
function updateShortcutsCount() {
    const countEl = document.getElementById('shortcuts-count');
    const count = (settings.custom_commands || []).filter(s => s.trigger && s.replacement).length;
    if (countEl) {
        countEl.textContent = count;
    }
}

// ============================================
// Vocabulary Modal
// ============================================

/**
 * Setup vocabulary editor modal
 */
function setupVocabularyModal() {
    const editBtn = document.getElementById('edit-vocabulary-btn');
    const modal = document.getElementById('vocabulary-modal');
    const closeBtn = document.getElementById('vocabulary-modal-close');
    const cancelBtn = document.getElementById('vocabulary-cancel');
    const saveBtn = document.getElementById('vocabulary-save');
    const addBtn = document.getElementById('add-vocabulary-btn');
    const input = document.getElementById('vocabulary-input');

    if (editBtn) {
        editBtn.addEventListener('click', () => {
            loadVocabularyList();
            openModal('vocabulary-modal');
        });
    }

    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('vocabulary-modal'));
    if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('vocabulary-modal'));

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            updateVocabularyCount();
            closeModal('vocabulary-modal');
            showToast('Vocabulary saved', 'success');
        });
    }

    if (addBtn && input) {
        addBtn.addEventListener('click', () => addVocabularyWord(input.value));
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addVocabularyWord(input.value);
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal('vocabulary-modal');
        });
    }
}

/**
 * Update vocabulary count display
 */
function updateVocabularyCount() {
    const countEl = document.getElementById('vocabulary-count');
    const count = (settings.custom_vocabulary || []).length;
    if (countEl) {
        countEl.textContent = count;
    }
}

// ============================================
// Filler Words Modal
// ============================================

/**
 * Setup filler words editor modal
 */
function setupFillersModal() {
    const editBtn = document.getElementById('edit-fillers-btn');
    const modal = document.getElementById('fillers-modal');
    const closeBtn = document.getElementById('fillers-modal-close');
    const cancelBtn = document.getElementById('fillers-cancel');
    const saveBtn = document.getElementById('fillers-save');
    const addBtn = document.getElementById('add-filler-btn');
    const input = document.getElementById('filler-input');

    if (editBtn) {
        editBtn.addEventListener('click', () => {
            loadFillerList();
            openModal('fillers-modal');
        });
    }

    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('fillers-modal'));
    if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('fillers-modal'));

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            updateFillerCount();
            closeModal('fillers-modal');
            showToast('Filler words saved', 'success');
        });
    }

    if (addBtn && input) {
        addBtn.addEventListener('click', () => addFillerWord(input.value));
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addFillerWord(input.value);
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal('fillers-modal');
        });
    }
}

/**
 * Update filler count display
 */
function updateFillerCount() {
    const countEl = document.getElementById('filler-count');
    const count = (settings.custom_fillers || []).length;
    if (countEl) {
        countEl.textContent = count;
    }
}

// ============================================
// History Modal
// ============================================

let historyData = [];
let selectedHistoryIndex = null;

/**
 * Setup history modal event handlers
 */
function setupHistoryModal() {
    const viewBtn = document.getElementById('view-history-btn');
    const modal = document.getElementById('history-modal');
    const closeBtn = document.getElementById('history-modal-close');
    const closeFooterBtn = document.getElementById('history-close');
    const clearBtn = document.getElementById('history-clear');
    const copyBtn = document.getElementById('history-copy');
    const exportBtn = document.getElementById('history-export');

    if (viewBtn) {
        viewBtn.addEventListener('click', async () => {
            selectedHistoryIndex = null;
            if (copyBtn) copyBtn.disabled = true;
            await loadHistory();
            renderHistoryList();
            openModal('history-modal');
        });
    }

    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('history-modal'));
    if (closeFooterBtn) closeFooterBtn.addEventListener('click', () => closeModal('history-modal'));

    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to clear all transcription history?')) {
                await clearHistory();
                selectedHistoryIndex = null;
                if (copyBtn) copyBtn.disabled = true;
                await loadHistory();
                renderHistoryList();
                updateHistoryCount();
                showToast('History cleared', 'success');
            }
        });
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', copySelectedHistory);
    }

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            showExportFormatModal();
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal('history-modal');
        });
    }

    // Setup export format modal
    setupExportFormatModal();

    // Initial count update
    updateHistoryCount();
}

/**
 * Setup export format modal handlers
 */
function setupExportFormatModal() {
    const modal = document.getElementById('export-format-modal');
    const closeBtn = document.getElementById('export-format-close');
    const cancelBtn = document.getElementById('export-format-cancel');
    const confirmBtn = document.getElementById('export-format-confirm');

    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('export-format-modal'));
    if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('export-format-modal'));

    if (confirmBtn) {
        confirmBtn.addEventListener('click', async () => {
            const selectedFormat = document.querySelector('input[name="export-format"]:checked')?.value || 'txt';
            closeModal('export-format-modal');
            await exportHistory(selectedFormat);
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal('export-format-modal');
        });
    }
}

/**
 * Load history from backend
 */
async function loadHistory() {
    try {
        if (window.pywebview && window.pywebview.api) {
            const result = await window.pywebview.api.get_history();
            historyData = result.history || [];
        } else {
            // Mock data for testing
            console.log('Mock: loading history');
            historyData = JSON.parse(localStorage.getItem('mock_history') || '[]');
        }
    } catch (error) {
        console.error('Failed to load history:', error);
        historyData = [];
    }
}

/**
 * Clear all history
 */
async function clearHistory() {
    try {
        if (window.pywebview && window.pywebview.api) {
            await window.pywebview.api.clear_history();
        } else {
            console.log('Mock: clearing history');
            localStorage.removeItem('mock_history');
        }
        historyData = [];
    } catch (error) {
        console.error('Failed to clear history:', error);
    }
}

/**
 * Show export format modal
 */
function showExportFormatModal() {
    // Reset to default selection (txt)
    const defaultRadio = document.querySelector('input[name="export-format"][value="txt"]');
    if (defaultRadio) defaultRadio.checked = true;
    openModal('export-format-modal');
}

/**
 * Export history to file with selected format
 */
async function exportHistory(formatType = 'txt') {
    try {
        if (window.pywebview && window.pywebview.api) {
            const result = await window.pywebview.api.export_history(formatType);
            if (result.success) {
                showToast('History exported to ' + result.filename, 'success');
            } else if (result.cancelled) {
                showToast('Export cancelled', 'info');
            } else {
                showToast('Export failed: ' + (result.error || 'Unknown error'), 'error');
            }
        } else {
            // Mock export - download based on format
            console.log('Mock: exporting history as ' + formatType);
            let content, mimeType, extension;

            if (formatType === 'txt') {
                content = "Transcription History\n" + "=".repeat(60) + "\n\n";
                historyData.forEach(item => {
                    content += `[${new Date(item.timestamp).toLocaleString()}]\n${item.text}\n\n`;
                });
                mimeType = 'text/plain';
                extension = 'txt';
            } else if (formatType === 'csv') {
                content = "Timestamp,Text,Characters\n";
                historyData.forEach(item => {
                    const text = item.text.replace(/"/g, '""');
                    content += `"${item.timestamp}","${text}",${item.text.length}\n`;
                });
                mimeType = 'text/csv';
                extension = 'csv';
            } else {
                content = JSON.stringify(historyData, null, 2);
                mimeType = 'application/json';
                extension = 'json';
            }

            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `transcription_history.${extension}`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('History exported', 'success');
        }
    } catch (error) {
        console.error('Failed to export history:', error);
        showToast('Failed to export history', 'error');
    }
}

/**
 * Render history list in modal
 */
function renderHistoryList() {
    const listEl = document.getElementById('history-list');
    const emptyEl = document.getElementById('history-empty');

    if (!listEl) return;

    if (historyData.length === 0) {
        listEl.innerHTML = '';
        if (emptyEl) emptyEl.classList.remove('hidden');
        return;
    }

    if (emptyEl) emptyEl.classList.add('hidden');

    listEl.innerHTML = historyData.map((item, index) => {
        const time = new Date(item.timestamp).toLocaleString();
        const selectedClass = selectedHistoryIndex === index ? ' selected' : '';
        return `
            <div class="history-item${selectedClass}" data-index="${index}">
                <div class="history-item-header">
                    <span class="history-item-time">${escapeHtml(time)}</span>
                </div>
                <div class="history-item-text">${escapeHtml(item.text)}</div>
            </div>
        `;
    }).join('');

    // Add click handlers to history items
    listEl.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index, 10);
            selectHistoryItem(index);
        });
    });
}

/**
 * Select a history item
 */
function selectHistoryItem(index) {
    selectedHistoryIndex = index;
    const copyBtn = document.getElementById('history-copy');

    // Update visual selection
    document.querySelectorAll('.history-item').forEach((el, i) => {
        el.classList.toggle('selected', i === index);
    });

    // Enable copy button
    if (copyBtn) copyBtn.disabled = false;
}

/**
 * Copy selected history item to clipboard
 */
async function copySelectedHistory() {
    if (selectedHistoryIndex === null || !historyData[selectedHistoryIndex]) {
        showToast('Please select a transcription first', 'warning');
        return;
    }

    const text = historyData[selectedHistoryIndex].text;
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success');
    } catch (err) {
        // Fallback for older browsers or when clipboard API is not available
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard', 'success');
        } catch (copyErr) {
            showToast('Failed to copy to clipboard', 'error');
        }
        document.body.removeChild(textarea);
    }
}

/**
 * Update history count display
 */
async function updateHistoryCount() {
    const countEl = document.getElementById('history-count');
    if (!countEl) return;

    try {
        if (window.pywebview && window.pywebview.api) {
            const result = await window.pywebview.api.get_history_count();
            const count = result.count || 0;
            countEl.textContent = `${count} transcription${count !== 1 ? 's' : ''} saved`;
        } else {
            const mockHistory = JSON.parse(localStorage.getItem('mock_history') || '[]');
            const count = mockHistory.length;
            countEl.textContent = `${count} transcription${count !== 1 ? 's' : ''} saved`;
        }
    } catch (error) {
        countEl.textContent = '0 transcriptions saved';
    }
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Ollama Connection Test
// ============================================

/**
 * Test Ollama connection
 */
async function testOllamaConnection() {
    const urlInput = document.getElementById('ollama-url');
    const badge = document.getElementById('ollama-status');
    const btn = document.getElementById('test-ollama-btn');
    const actionRow = document.getElementById('ollama-action-row');

    if (!urlInput || !badge) return;

    const url = urlInput.value.trim();
    if (!url) {
        showToast('Please enter an Ollama URL', 'error');
        return;
    }

    // Update UI to testing state
    badge.className = 'status-badge checking';
    badge.querySelector('.status-text').textContent = 'Testing...';
    if (btn) btn.disabled = true;
    if (actionRow) actionRow.style.display = 'none';

    try {
        const result = await pywebview.api.test_ollama_connection(url);
        if (result.success && result.data.connected) {
            badge.className = 'status-badge available';
            badge.querySelector('.status-text').textContent = 'Connected';
            showToast('Ollama connection successful', 'success');
            if (actionRow) actionRow.style.display = 'none';
        } else {
            badge.className = 'status-badge unavailable';
            badge.querySelector('.status-text').textContent = result.error || 'Connection failed';
            showToast('Could not connect to Ollama', 'error');
            if (actionRow) actionRow.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error testing Ollama:', error);
        badge.className = 'status-badge unavailable';
        badge.querySelector('.status-text').textContent = 'Error';
        showToast('Connection test failed', 'error');
        if (actionRow) actionRow.style.display = 'flex';
    } finally {
        if (btn) btn.disabled = false;
    }
}

// ============================================
// Reset to Defaults
// ============================================

/**
 * Show confirmation and reset settings
 */
async function confirmResetDefaults() {
    if (!confirm('Reset all settings to defaults? This cannot be undone.')) {
        return;
    }

    try {
        const result = await pywebview.api.reset_to_defaults();
        if (result.success) {
            showToast('Settings reset to defaults', 'success');
            // Reload settings
            await loadSettings();
        } else {
            showToast('Failed to reset: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        showToast('Failed to reset settings', 'error');
    }
}

// ============================================
// About Page Functions
// ============================================

/**
 * Load version and system info
 */
async function loadAboutInfo() {
    try {
        const result = await pywebview.api.get_version_info();
        if (result.success) {
            const versionEl = document.getElementById('about-version');
            const pythonEl = document.getElementById('about-python');

            if (versionEl) versionEl.textContent = result.data.version;
            if (pythonEl) pythonEl.textContent = result.data.python_version;
        }
    } catch (error) {
        console.error('Error loading version info:', error);
    }
}

/**
 * Load and display license status
 */
async function loadLicenseStatus() {
    try {
        const result = await pywebview.api.get_license_status();
        if (result.success) {
            const badge = document.getElementById('license-badge');
            const title = document.getElementById('license-title');
            const subtitle = document.getElementById('license-subtitle');
            const inputRow = document.getElementById('license-input-row');

            if (result.data.is_active) {
                badge.className = 'license-badge active';
                title.textContent = 'Licensed';
                subtitle.textContent = 'Full version activated';
                // Hide license input for active licenses
                if (inputRow) inputRow.classList.add('hidden');
            } else if (result.data.is_trial) {
                badge.className = 'license-badge trial';
                title.textContent = 'Trial Mode';
                const days = result.data.days_remaining;
                subtitle.textContent = days !== null
                    ? `${days} day${days !== 1 ? 's' : ''} remaining`
                    : 'Trial period';
            } else {
                badge.className = 'license-badge';
                title.textContent = 'Not Licensed';
                subtitle.textContent = 'Please activate or purchase';
            }
        }
    } catch (error) {
        console.error('Error loading license status:', error);
    }
}

/**
 * Activate a license key
 */
async function activateLicense(key) {
    key = key.trim();
    if (!key) {
        showToast('Please enter a license key', 'error');
        return;
    }

    const btn = document.getElementById('activate-license-btn');
    if (btn) btn.disabled = true;

    try {
        const result = await pywebview.api.activate_license(key);
        if (result.success) {
            showToast('License activated successfully!', 'success');
            // Clear input and refresh status
            const input = document.getElementById('license-key');
            if (input) input.value = '';
            await loadLicenseStatus();
        } else {
            showToast(result.error || 'Invalid license key', 'error');
        }
    } catch (error) {
        console.error('Error activating license:', error);
        showToast('Failed to activate license', 'error');
    } finally {
        if (btn) btn.disabled = false;
    }
}

// ============================================
// UI Feedback
// ============================================

/**
 * Show "Saved" status in sidebar
 */
function showSaveStatus() {
    const status = document.getElementById('save-status');
    if (status) {
        status.textContent = '✓ Saved';
        status.classList.add('visible');

        // Clear any existing timeout
        if (saveTimeout) clearTimeout(saveTimeout);

        // Hide after 2 seconds
        saveTimeout = setTimeout(() => {
            status.classList.remove('visible');
        }, 2000);
    }
}

/**
 * Show a toast notification
 */
let toastTimeout = null;

function showToast(message, type = 'info') {
    console.log('showToast called with:', message, type);
    const toast = document.getElementById('toast');
    console.log('Toast element:', toast);
    if (toast) {
        // Clear any existing timeout
        if (toastTimeout) {
            clearTimeout(toastTimeout);
        }

        toast.textContent = message;
        toast.className = 'toast visible ' + type;
        console.log('Toast shown with classes:', toast.className);

        // Auto-dismiss after 3 seconds
        toastTimeout = setTimeout(() => {
            toast.classList.remove('visible');
        }, 3000);
    } else {
        console.error('Toast element not found!');
    }
}

/**
 * Hide toast immediately (click to dismiss)
 */
function hideToast() {
    const toast = document.getElementById('toast');
    if (toast) {
        if (toastTimeout) {
            clearTimeout(toastTimeout);
            toastTimeout = null;
        }
        toast.classList.remove('visible');
    }
}

// ============================================
// Keyboard Navigation
// ============================================

/**
 * Set up keyboard navigation
 */
function setupKeyboardNavigation() {
    const tabs = ['general', 'audio', 'recognition', 'text', 'advanced', 'about'];

    document.addEventListener('keydown', (e) => {
        // Escape key - close modals and banners
        if (e.key === 'Escape') {
            // Close welcome banner
            const banner = document.getElementById('welcome-banner');
            if (banner && banner.classList.contains('visible')) {
                hideWelcomeBanner();
                return;
            }
            // Close any open modal
            const openModal = document.querySelector('.modal-overlay.visible');
            if (openModal) {
                closeModal(openModal.id);
                return;
            }
        }

        // Ctrl+1-6 - Quick tab switching
        if (e.ctrlKey && !e.shiftKey && !e.altKey && e.key >= '1' && e.key <= '6') {
            e.preventDefault();
            const tabIndex = parseInt(e.key) - 1;
            if (tabIndex < tabs.length) {
                navigateTo(tabs[tabIndex]);
            }
        }

        // Ctrl+S - Save confirmation (settings auto-save, but provide feedback)
        if (e.ctrlKey && !e.shiftKey && !e.altKey && e.key === 's') {
            e.preventDefault();
            showToast('Settings auto-saved', 'success');
        }

        // Arrow keys for tab navigation when focused on nav
        if (e.target.closest('.nav-items')) {
            const navItems = Array.from(document.querySelectorAll('.nav-item'));
            const currentIndex = navItems.indexOf(document.activeElement);

            if (e.key === 'ArrowDown' && currentIndex < navItems.length - 1) {
                e.preventDefault();
                navItems[currentIndex + 1].focus();
            } else if (e.key === 'ArrowUp' && currentIndex > 0) {
                e.preventDefault();
                navItems[currentIndex - 1].focus();
            } else if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                document.activeElement.click();
            }
        }
    });
}

// ============================================
// Welcome Banner
// ============================================

/**
 * Check if this is first run and show welcome banner
 * Now reads from backend config instead of localStorage for reliable persistence
 */
async function checkFirstRun() {
    // Check backend config instead of localStorage
    if (!settings.onboarding_complete) {
        showWelcomeBanner();
    }
}

/**
 * Show the welcome banner
 */
function showWelcomeBanner() {
    const banner = document.getElementById('welcome-banner');
    if (banner) {
        banner.classList.add('visible');
    }
}

/**
 * Hide the welcome banner and mark as seen
 * Now saves to backend config instead of localStorage for reliable persistence
 */
async function hideWelcomeBanner() {
    const banner = document.getElementById('welcome-banner');
    const dontShowAgain = document.getElementById('dont-show-again');
    if (banner) {
        banner.classList.remove('visible');
        if (dontShowAgain && dontShowAgain.checked) {
            // Save to backend config instead of localStorage
            await saveSetting('onboarding_complete', true);
        }
    }
}

// ============================================
// Mock API (for browser testing)
// ============================================

function createMockApi() {
    const mockSettings = {
        hotkey: { ctrl: true, shift: true, alt: false, key: 'space' },
        recording_mode: 'push_to_talk',
        language: 'en',
        start_with_windows: false,
        model_size: 'medium',
        processing_mode: 'auto',
        silence_duration_sec: 2.0,
        custom_vocabulary: ['MurmurTone', 'PyWebView'],
        sample_rate: 16000,
        input_device: null,
        noise_gate_enabled: true,
        noise_gate_threshold_db: -40,
        audio_feedback_volume: 50,
        sound_processing: true,
        sound_success: true,
        sound_error: true,
        sound_command: true,
        auto_paste: true,
        paste_mode: 'clipboard',
        voice_commands_enabled: true,
        scratch_that_enabled: true,
        filler_removal_enabled: true,
        filler_removal_aggressive: false,
        custom_fillers: ['actually', 'basically'],
        ai_cleanup_enabled: true,
        ollama_url: 'http://localhost:11434',
        ollama_model: 'llama3.2:3b',
        ai_cleanup_mode: 'formality',
        ai_formality_level: 'casual',
        preview_enabled: true,
        preview_position: 'bottom_right',
        preview_auto_hide_delay: 2.0
    };

    return {
        api: {
            get_all_settings: () => Promise.resolve({ success: true, data: mockSettings }),
            save_setting: (key, value) => {
                console.log(`Mock save: ${key} = ${value}`);
                return Promise.resolve({ success: true });
            },
            get_version_info: () => Promise.resolve({
                success: true,
                data: { app_name: 'MurmurTone', version: '1.0.0', python_version: '3.12.0' }
            }),
            get_audio_devices: () => Promise.resolve({
                success: true,
                data: [
                    { name: 'System Default (Microphone)', id: null, is_default: true },
                    { name: 'Microphone (Realtek Audio)', id: 'realtek-mic', is_default: false },
                    { name: 'Blue Yeti', id: 'blue-yeti', is_default: false }
                ]
            }),
            get_available_models: () => Promise.resolve({
                success: true,
                data: [
                    { name: 'tiny', display_name: 'Quick', size_mb: 75, is_bundled: true, is_downloaded: true },
                    { name: 'small', display_name: 'Recommended', size_mb: 484, is_bundled: false, is_downloaded: false }
                ]
            }),
            get_license_status: () => Promise.resolve({
                success: true,
                data: { status: 'trial', is_trial: true, is_active: false, days_remaining: 14 }
            }),
            get_gpu_status: () => Promise.resolve({
                success: true,
                data: { available: true, name: 'NVIDIA GeForce RTX 3080' }
            }),
            test_ollama_connection: (url) => Promise.resolve({
                success: true,
                data: { connected: true }
            }),
            reset_to_defaults: () => Promise.resolve({ success: true }),
            activate_license: (key) => {
                console.log(`Mock activate license: ${key}`);
                if (key && key.length > 10) {
                    return Promise.resolve({ success: true, data: { status: 'active' } });
                }
                return Promise.resolve({ success: false, error: 'Invalid license key' });
            },
            open_url: (url) => {
                console.log(`Mock open URL: ${url}`);
                window.open(url, '_blank');
                return Promise.resolve({ success: true });
            },
            get_history_count: () => {
                const mockHistory = JSON.parse(localStorage.getItem('mock_history') || '[]');
                return Promise.resolve({ success: true, count: mockHistory.length });
            }
        }
    };
}

// ============================================
// Start
// ============================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
