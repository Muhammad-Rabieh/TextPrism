/* ═══════════════════════════════════════════════════════════
   TextPrism Project — Frontend Logic (script.js)
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM Elements ──
    const textInput = document.getElementById('text-input');
    const clearBtn = document.getElementById('clear-btn');
    const pasteMainBtn = document.getElementById('paste-main-btn');
    const outputContent = document.getElementById('output-content');
    const downloadBtn = document.getElementById('download-html-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const downloadMdBtn = document.getElementById('download-md-btn');
    const copyBtn = document.getElementById('copy-btn');
    console.log('TextPrism Script v1.3 initialized. PDF Button exists:', !!downloadPdfBtn);




    // Modal


    // Unified Magic Prompt Elements
    const magicPromptModal = document.getElementById('magic-prompt-modal');
    const magicPromptBtn = document.getElementById('magic-prompt-btn');
    const magicPromptText = document.getElementById('magic-prompt-text');
    const copyMagicBtn = document.getElementById('copy-magic-btn');
    const pasteAiBtn = document.getElementById('paste-ai-btn');
    const aiResponseInput = document.getElementById('ai-response-input');
    const processAiBtn = document.getElementById('process-ai-btn');
    const magicModalCloseBtn = document.getElementById('magic-modal-close');

    let activeShape = 'box';
    let lastGeneratedHTML = '';
    let lastVisualSourceText = ''; // New: Store the AI raw text used for the last render

    /* AI Tier Selection removed */

    // Generic Indicator Update function
    function updateIndicator(selectorId, indicatorId) {
        const indicator = document.getElementById(indicatorId);
        if (!indicator) return;
        const activeOpt = document.querySelector(`#${selectorId} .format-option.active`);
        if (activeOpt) {
            indicator.style.width = activeOpt.offsetWidth + 'px';
            indicator.style.left = activeOpt.offsetLeft + 'px';
        }
    }

    // Chart format selector logic
    const chartFormatOptions = document.querySelectorAll('#chart-format-selector .format-option');
    chartFormatOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            chartFormatOptions.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            updateIndicator('chart-format-selector', 'format-indicator');
        });
    });

    // Style selector logic
    const styleOptions = document.querySelectorAll('#style-selector .format-option');
    styleOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            styleOptions.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            updateIndicator('style-selector', 'style-indicator');
        });
    });

    // Language selector logic
    let currentLanguage = 'english';
    const languageOptions = document.querySelectorAll('#language-selector .format-option');
    languageOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            languageOptions.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            currentLanguage = opt.dataset.value;
            updateIndicator('language-selector', 'language-indicator');
        });
    });

    // Initial position & Resize handling
    const refreshIndicators = () => {
        updateIndicator('chart-format-selector', 'format-indicator');
        updateIndicator('style-selector', 'style-indicator');
        updateIndicator('language-selector', 'language-indicator');
    };

    window.addEventListener('load', refreshIndicators);
    window.addEventListener('resize', refreshIndicators);
    // Trigger multiple times to catch layout settled state
    refreshIndicators();
    setTimeout(refreshIndicators, 50);
    setTimeout(refreshIndicators, 300);

    // ── Magic Prompt Workflow (2-Phase) ──
    if (magicPromptBtn) {
        magicPromptBtn.addEventListener('click', async () => {
            const text = textInput.value.trim();
            if (!text) {
                textInput.focus();
                return;
            }

            magicPromptBtn.disabled = true;
            try {
                const chartFormatActive = document.querySelector('#chart-format-selector .format-option.active');
                const chartFormat = chartFormatActive ? chartFormatActive.dataset.value : 'ascii';
                const styleActive = document.querySelector('#style-selector .format-option.active');
                const style = styleActive ? styleActive.dataset.value : 'visual';
                const langActive = document.querySelector('#language-selector .format-option.active');
                const language = langActive ? langActive.dataset.value : 'english';

                const response = await fetch('/magic-prompt/unified', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, chart_format: chartFormat, style: style, language: language })
                });
                const data = await response.json();

                if (magicPromptText) {
                    magicPromptText.textContent = data.prompt;
                    aiResponseInput.value = ''; // Clear previous
                    magicPromptModal.style.display = 'flex';
                }
            } catch (err) {
                console.error('Unified Prompt error:', err);
                alert('Failed to generate prompt.');
            } finally {
                magicPromptBtn.disabled = false;
            }
        });
    }

    if (copyMagicBtn) {
        copyMagicBtn.addEventListener('click', () => {
            const textToCopy = magicPromptText.innerText || magicPromptText.textContent;
            copyTextToClipboard(textToCopy).then(() => {
                copyMagicBtn.textContent = 'Copied!';
                copyMagicBtn.classList.add('btn-accent');
                setTimeout(() => {
                    copyMagicBtn.textContent = 'Copy Prompt';
                    copyMagicBtn.classList.remove('btn-accent');
                }, 2000);
            });
        });
    }

    magicModalCloseBtn.addEventListener('click', () => {
        magicPromptModal.style.display = 'none';
    });

    // ── Main Page Paste Button (Overlay Technique) ──
    if (pasteMainBtn) {
        const mainPasteOverlay = document.createElement('textarea');
        mainPasteOverlay.style.position = 'absolute';
        mainPasteOverlay.style.opacity = '0';
        mainPasteOverlay.style.cursor = 'pointer';
        mainPasteOverlay.style.zIndex = '10';
        mainPasteOverlay.style.top = '0';
        mainPasteOverlay.style.left = '0';
        mainPasteOverlay.style.width = '100%';
        mainPasteOverlay.style.height = '100%';
        mainPasteOverlay.style.border = 'none';
        mainPasteOverlay.style.background = 'transparent';
        mainPasteOverlay.style.resize = 'none';
        mainPasteOverlay.setAttribute('tabindex', '0');
        pasteMainBtn.style.position = 'relative';
        pasteMainBtn.style.overflow = 'hidden';
        pasteMainBtn.appendChild(mainPasteOverlay);

        pasteMainBtn.addEventListener('click', () => mainPasteOverlay.focus());

        mainPasteOverlay.addEventListener('focus', () => {
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const shortcut = isMac ? 'Cmd+V' : 'Ctrl+V';
            const oldChildren = Array.from(pasteMainBtn.children).filter(c => c !== mainPasteOverlay);
            oldChildren.forEach(c => c.style.display = 'none');
            const hint = document.createElement('span');
            hint.id = 'paste-main-hint';
            hint.style.fontWeight = '600';
            hint.style.color = 'var(--accent-primary)';
            hint.style.pointerEvents = 'none';
            hint.textContent = `Press ${shortcut}`;
            pasteMainBtn.insertBefore(hint, mainPasteOverlay);
            mainPasteOverlay.addEventListener('blur', function blurHandler() {
                const h = document.getElementById('paste-main-hint');
                if (h) h.remove();
                oldChildren.forEach(c => c.style.display = '');
                mainPasteOverlay.removeEventListener('blur', blurHandler);
            });
        });

        mainPasteOverlay.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text');
            if (text) {
                textInput.value = text;
                const h = document.getElementById('paste-main-hint');
                if (h) h.remove();
                const oldChildren = Array.from(pasteMainBtn.children).filter(c => c !== mainPasteOverlay);
                oldChildren.forEach(c => c.style.display = '');
                pasteMainBtn.innerHTML = '<img src="/icons/heroicons/check.svg" alt="" class="btn-icon" style="filter: brightness(0) opacity(0.6); width: 14px; height: 14px; margin-right: 4px;"> Pasted!';
                pasteMainBtn.appendChild(mainPasteOverlay);
                setTimeout(() => mainPasteOverlay.blur(), 2000);
            }
        });
    }

    if (pasteAiBtn) {
        // Create a transparent textarea overlay on top of the button
        const pasteOverlay = document.createElement('textarea');
        pasteOverlay.style.position = 'absolute';
        pasteOverlay.style.opacity = '0';
        pasteOverlay.style.cursor = 'pointer';
        pasteOverlay.style.zIndex = '10';
        pasteOverlay.style.top = '0';
        pasteOverlay.style.left = '0';
        pasteOverlay.style.width = '100%';
        pasteOverlay.style.height = '100%';
        pasteOverlay.style.border = 'none';
        pasteOverlay.style.background = 'transparent';
        pasteOverlay.style.resize = 'none';
        pasteOverlay.setAttribute('tabindex', '0');
        pasteAiBtn.style.position = 'relative';
        pasteAiBtn.style.overflow = 'hidden';
        pasteAiBtn.appendChild(pasteOverlay);

        // When the button is clicked, focus the overlay so it can receive Ctrl+V
        pasteAiBtn.addEventListener('click', (e) => {
            pasteOverlay.focus();
        });

        pasteOverlay.addEventListener('focus', () => {
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const shortcut = isMac ? 'Cmd+V' : 'Ctrl+V';
            pasteAiBtn.setAttribute('data-original-text', pasteAiBtn.innerText);
            const oldChildren = Array.from(pasteAiBtn.children).filter(c => c !== pasteOverlay);
            oldChildren.forEach(c => c.style.display = 'none');
            const hint = document.createElement('span');
            hint.id = 'paste-hint';
            hint.style.fontWeight = '600';
            hint.style.color = 'var(--accent-primary)';
            hint.style.pointerEvents = 'none';
            hint.textContent = `Press ${shortcut}`;
            pasteAiBtn.insertBefore(hint, pasteOverlay);

            pasteOverlay.addEventListener('blur', function blurHandler() {
                const h = document.getElementById('paste-hint');
                if (h) h.remove();
                oldChildren.forEach(c => c.style.display = '');
                pasteOverlay.removeEventListener('blur', blurHandler);
            });
        });

        pasteOverlay.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text');
            if (text) {
                aiResponseInput.value = text;
                const h = document.getElementById('paste-hint');
                if (h) h.remove();
                const oldChildren = Array.from(pasteAiBtn.children).filter(c => c !== pasteOverlay);
                oldChildren.forEach(c => c.style.display = '');
                pasteAiBtn.innerHTML = '<img src="/icons/heroicons/check.svg" alt="" class="btn-icon" style="filter: brightness(0) opacity(0.6); width: 14px; height: 14px; margin-right: 4px;"> Pasted!';
                pasteAiBtn.appendChild(pasteOverlay);
                setTimeout(() => {
                    pasteOverlay.blur();
                }, 2000);
            }
        });
    }

    // ── Helper: Copy Text ──
    function copyTextToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            return new Promise((resolve, reject) => {
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.top = "0";
                textArea.style.left = "0";
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    const successful = document.execCommand('copy');
                    if (successful) resolve();
                    else reject(new Error('Fallback: Copy command was unsuccessful'));
                } catch (err) {
                    reject(err);
                }
                document.body.removeChild(textArea);
            });
        }
    }
    /* Legacy event listeners removed for One-Phase Magic workflow */

    processAiBtn.onclick = async () => {
        const json = aiResponseInput.value.trim();
        if (!json) {
            aiResponseInput.focus();
            return;
        }

        processAiBtn.disabled = true;
        processAiBtn.textContent = '... Explaining ...';

        try {
            const formData = new FormData();
            formData.append('data', json);
            const langActive = document.querySelector('#language-selector .format-option.active');
            const language = langActive ? langActive.dataset.value : 'english';
            formData.append('language', language);

            const response = await fetch('/render-magic', { method: 'POST', body: formData });
            const html = await response.text();

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const explanationBody = doc.querySelector('.explanation-wrapper');

            if (explanationBody) {
                outputContent.innerHTML = explanationBody.innerHTML;
            } else {
                outputContent.innerHTML = html;
            }

            // Trigger Mermaid if present
            document.dispatchEvent(new CustomEvent('mermaid-refresh'));

            lastGeneratedHTML = html;
            lastVisualSourceText = json; // Preserve for high-quality export
            downloadBtn.disabled = false;
            if (downloadPdfBtn) downloadPdfBtn.disabled = false;
            downloadMdBtn.disabled = false;
            copyBtn.disabled = false;
            magicPromptModal.style.display = 'none';
            aiResponseInput.value = '';
        } catch (err) {
            console.error('Magic render error:', err);
            // If the error has a response body text, use it, otherwise generic alert
            const errorMsg = err.message || 'Failed to render AI response. Ensure it is valid JSON.';
            alert(errorMsg);
        } finally {
            processAiBtn.disabled = false;
            processAiBtn.textContent = 'Build Visual Explanation';
        }
    };



    /* Explain Form submit handler removed - now using Magic Prompt workflow */

    // ── Clear Button ──
    clearBtn.addEventListener('click', () => {
        textInput.value = '';
        if (aiResponseInput) aiResponseInput.value = '';

        outputContent.innerHTML = `
                <div class="output-placeholder">
                    <img src="/icons/openmoji/1F3B8.png" alt="art" width="72" height="72" class="placeholder-emoji">
                            <p>Your visual explanation will appear here</p>
                        <p class="placeholder-sub">Paste text on the left and click "Explain & Map with AI"</p>
                    </div>
            `;

        // Reset Paste Buttons Labels if they were changed (e.g. to "Pasted!")
        const initialPasteHTML = `
            <img src="/icons/heroicons/clipboard.svg" alt="" class="btn-icon"
                style="filter: brightness(0) opacity(0.6); width: 14px; height: 14px; margin-right: 4px;">
            Paste
        `;

        if (pasteMainBtn) {
            const overlay = pasteMainBtn.querySelector('textarea');
            pasteMainBtn.innerHTML = initialPasteHTML;
            if (overlay) pasteMainBtn.appendChild(overlay);
        }
        if (pasteAiBtn) {
            const overlay = pasteAiBtn.querySelector('textarea');
            pasteAiBtn.innerHTML = initialPasteHTML;
            if (overlay) pasteAiBtn.appendChild(overlay);
        }

        downloadBtn.disabled = true;
        if (downloadPdfBtn) downloadPdfBtn.disabled = true;
        downloadMdBtn.disabled = true;
        copyBtn.disabled = true;
        lastGeneratedHTML = '';
        textInput.focus();
    });

    // ── Helper: Get Export Filename from Generated Title ──
    function getExportFilename(extension) {
        // Try to read the title from the first meaningful heading in the output
        const titleEl = outputContent.querySelector(
            'h1, h2, h3, .doc-title, .banner-title, .ascii-title, .section-title, [class*="title"]'
        );
        let rawTitle = (titleEl && titleEl.textContent.trim()) || '';

        // Fallback: grab first non-empty text node from output
        if (!rawTitle) {
            const walker = document.createTreeWalker(outputContent, NodeFilter.SHOW_TEXT);
            let node;
            while ((node = walker.nextNode())) {
                const t = node.nodeValue.trim().replace(/[★●•►▸→]/g, '').trim();
                if (t.length > 2) { rawTitle = t; break; }
            }
        }

        // Sanitize: take first 3 meaningful words, strip special chars
        const words = rawTitle
            .replace(/[^a-zA-Z0-9\s\-]/g, ' ')
            .trim()
            .split(/\s+/)
            .filter(w => w.length > 0)
            .slice(0, 3);

        const baseName = words.length > 0 ? words.join('_') : 'TextPrism_Export';

        // Suffix with active chart type — SCOPED to chart format selector
        const chartFormatActive = document.querySelector('#chart-format-selector .format-option.active');
        const chartFormat = chartFormatActive ? chartFormatActive.dataset.value.toUpperCase() : 'ASCII';

        return `${baseName}_${chartFormat}.${extension}`;
    }

    // ── Helper: Download Data ──
    function downloadFile(content, fileName, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);
    }

    // ── Download HTML ──
    downloadBtn.addEventListener('click', () => {
        if (!lastGeneratedHTML) return;

        // Fix relative paths for local viewing
        const origin = window.location.origin;
        let standaloneHTML = lastGeneratedHTML
            .replace(/src="\//g, `src="${origin}/`)
            .replace(/href="\//g, `href="${origin}/`);

        // Ensure UTF-8 meta is present and clean
        if (!standaloneHTML.includes('<meta charset="UTF-8">')) {
            standaloneHTML = standaloneHTML.replace('<head>', '<head><meta charset="UTF-8">');
        }

        downloadFile(standaloneHTML, getExportFilename('html'), 'text/html;charset=utf-8');
    });

    // ── Download PDF (Server-Side via Playwright) ──
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', async () => {
            const element = outputContent;
            if (!element || !element.innerHTML.trim() || element.querySelector('.output-placeholder')) {
                alert('No content to export as PDF.');
                return;
            }

            const originalHTML = downloadPdfBtn.innerHTML;
            downloadPdfBtn.disabled = true;
            downloadPdfBtn.innerHTML = '<span class="spinner-sm"></span> Generating...';

            try {
                // Build a full standalone HTML document with embedded styles
                // that Chrome's print engine will properly paginate
                const computedBg = window.getComputedStyle(document.documentElement)
                    .getPropertyValue('--bg-primary').trim() || '#f8fafc';

                // Grab ALL stylesheets from the current page for faithful rendering
                let allStyles = '';
                for (const sheet of document.styleSheets) {
                    try {
                        for (const rule of sheet.cssRules) {
                            allStyles += rule.cssText + '\n';
                        }
                    } catch (e) {
                        // Cross-origin sheets can't be read, skip
                    }
                }

                // Convert relative icon URLs to absolute
                const origin = window.location.origin;
                let contentHTML = element.innerHTML
                    .replace(/src="\//g, `src="${origin}/`)
                    .replace(/href="\//g, `href="${origin}/`);

                const fullHTML = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        ${allStyles}

        /* ── PDF Print Overrides ── */
        @page {
            size: A4;
            margin: 15mm 12mm;
        }

        body {
            /* Forced fallback to universally safe system fonts. 
               Chromium PDF exporter historically calculates extremely tight 
               mathematical bounding boxes for custom Web Fonts (like Inter), 
               causing selection tools and PDF parsers to clip start/end/top/bottom of words. */
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            background: white !important;
            color: #0f172a;
            padding: 0;
            margin: 0;
            line-height: 1.7;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        .output-content {
            max-width: 100%;
            padding: 0;
        }

        /* Force page break BEFORE each section */
        .section-block {
            page-break-before: always;
            break-before: page;
            margin-top: 0;
        }

        /* First section should NOT have a page break before it */
        .section-block:first-of-type {
            page-break-before: auto;
            break-before: auto;
        }

        /* Never split these leaf elements across pages */
        .sentence-item,
        .ascii-box,
        .ascii-flow,
        .ascii-callout,
        .ascii-sentence,
        .ascii-banner,
        .section-separator,
        .section-header,
        .section-text,
        .summary-box,
        .explanation-box,
        .bullet-list li,
        pre {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }

        /* Hide interactive elements */
        .no-print, .action-buttons, button { display: none !important; }

        /* Ensure dark-mode colors print properly */
        .section-block { background: white; }
        
        /* Bulletproof Block Layout to prevent Chromium Flexbox clipping */
        .sentence-item { 
            display: block !important;
            background: white !important; 
            border: 1px solid #e2e8f0 !important;
            border-left: 4px solid #3b82f6 !important;
            margin-bottom: 16px !important;
            padding: 18px 20px !important;
            overflow: visible !important;
            page-break-inside: avoid !important;
        }
        /* Defeat the inline inline-styles from explanation.html */
        .sentence-item > div,
        .sentence-item > div > div {
            display: block !important;
            overflow: visible !important;
        }
        .sentence-icon {
            float: left !important;
            margin-right: 18px !important;
            margin-bottom: 4px !important;
            margin-top: 2px !important;
        }
        .sentence-text {
            display: block !important;
            line-height: 1.8 !important; 
            padding-top: 10px !important; 
            padding-bottom: 10px !important; 
            margin-top: -10px !important;
            margin-bottom: -10px !important;
            overflow: visible !important;
        }
        
        /* Universal Paint-Box Expansion to fix all Chromium text clipping tops/bottoms */
        h1, h2, h3, p, li, .section-text {
            padding-top: 8px !important;
            padding-bottom: 8px !important;
            margin-top: -8px !important;
            margin-bottom: -8px !important;
            overflow: visible !important;
        }
        
        /* ── PDF Font Size Enhancements for Readability ── */
        .title-section h1 { font-size: 32px !important; }
        .explanation-box h2 { font-size: 22px !important; margin-bottom: 12px !important; }
        .section-header h1 { font-size: 28px !important; }
        .section-header h2 { font-size: 24px !important; }
        .section-header h3 { font-size: 20px !important; }
        .sentence-text, .section-text, .bullet-list li { font-size: 18px !important; line-height: 1.8 !important; }
        .explanation-box .section-text { font-size: 20px !important; line-height: 1.8 !important; }
        
        .ascii-sentence {
            clear: both !important;
            margin-top: 16px !important;
            display: block !important;
        }
        .sentence-item::after {
            content: "";
            display: table;
            clear: both;
        }
        pre, .ascii-box, .ascii-flow, .ascii-callout, .ascii-sentence {
            background: #f8fafc !important;
            border: 1px solid #e2e8f0;
            color: #0f172a;
        }
    </style>
</head>
<body>
    <div class="output-content">
        ${contentHTML}
    </div>
</body>
</html>`;

                // Send to server for Playwright-based PDF generation
                const response = await fetch('/export-pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ html: fullHTML })
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.error || 'Server PDF generation failed');
                }

                // Download the returned PDF
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = getExportFilename('pdf');
                a.style.display = 'none';
                document.body.appendChild(a);
                a.click();
                setTimeout(() => {
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 100);

            } catch (err) {
                console.error('PDF Export error:', err);
                alert(`Failed to export PDF: ${err.message}`);
            } finally {
                downloadPdfBtn.disabled = false;
                downloadPdfBtn.innerHTML = originalHTML;
            }
        });
    }

    // ── Download Markdown ──
    downloadMdBtn.addEventListener('click', async () => {
        // Use lastVisualSourceText if available (the rich AI response), 
        // fall back to textInput for simple heuristic renders.
        const text = (lastVisualSourceText || textInput.value).trim();
        if (!text) return;

        downloadMdBtn.disabled = true;
        const originalText = downloadMdBtn.innerHTML;
        downloadMdBtn.innerHTML = '<span class="spinner-sm"></span>';

        try {
            const formData = new FormData();
            formData.append('text', text);

            const response = await fetch('/export-md', { method: 'POST', body: formData });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to export Markdown.');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = getExportFilename('zip');
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('Markdown Export: Error:', err);
            alert('Failed to export Markdown.');
        } finally {
            downloadMdBtn.disabled = false;
            downloadMdBtn.innerHTML = originalText;
        }
    });

    // ── Copy Output ──
    copyBtn.addEventListener('click', () => {
        const text = outputContent.innerText;
        copyTextToClipboard(text).then(() => {
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<img src="/icons/heroicons/check.svg" alt="" class="btn-icon"> Copied!';
            setTimeout(() => { copyBtn.innerHTML = originalHTML; }, 2000);
        }).catch(err => {
            console.error('Copy Output: Failed:', err);
            alert('Failed to copy natively. Please copy manually.');
        });
    });

    // ── Keyboard Shortcuts ──
    document.addEventListener('keydown', (e) => {
        // Escape: close modal

        // Ctrl+Enter: Trigger Magic Prompt
        if (e.ctrlKey && e.key === 'Enter' && document.activeElement === textInput) {
            e.preventDefault();
            magicPromptBtn.click();
        }
    });
});
