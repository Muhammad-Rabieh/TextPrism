/* ═══════════════════════════════════════════════════════════
   Text Explain Project — Frontend Logic (script.js)
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM Elements ──
    const explainForm = document.getElementById('explain-form');
    const textInput = document.getElementById('text-input');
    const explainBtn = document.getElementById('explain-btn');
    const clearBtn = document.getElementById('clear-btn');
    const outputContent = document.getElementById('output-content');
    const downloadBtn = document.getElementById('download-html-btn');
    const downloadMdBtn = document.getElementById('download-md-btn');
    const copyBtn = document.getElementById('copy-btn');

    // SHAPE_IT controls
    const shapeButtons = document.querySelectorAll('.shape-btn');
    const shapeTextInput = document.getElementById('shape-text-input');
    const shapeStyleSelect = document.getElementById('shape-style-select');
    const generateShapeBtn = document.getElementById('generate-shape-btn');
    const quickAddShapeBtn = document.getElementById('quick-add-shape-btn');

    // Icon lookup
    const iconSearchInput = document.getElementById('icon-search-input');
    const iconSearchBtn = document.getElementById('icon-search-btn');
    const iconSearchResult = document.getElementById('icon-search-result');

    // Modal
    const shapeModal = document.getElementById('shape-preview-modal');
    const shapePreviewOutput = document.getElementById('shape-preview-output');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const copyShapeBtn = document.getElementById('copy-shape-btn');
    const insertShapeBtn = document.getElementById('insert-shape-btn');

    // Magic Prompt Modal Elements
    const magicPromptModal = document.getElementById('magic-prompt-modal');
    const magicPromptBtn = document.getElementById('magic-prompt-btn');
    const magicModalCloseBtn = document.getElementById('magic-modal-close-btn');

    // Containers
    const phase1Container = document.getElementById('phase1-container');
    const phase2Container = document.getElementById('phase2-container');

    // Prompts
    const phase1PromptText = document.getElementById('magic-prompt-phase1-text');
    const phase2PromptText = document.getElementById('magic-prompt-phase2-text');

    // Buttons
    const copyPhase1Btn = document.getElementById('copy-phase1-btn');
    const copyPhase2Btn = document.getElementById('copy-phase2-btn');
    const gotoPhase2Btn = document.getElementById('goto-phase2-btn');
    const backToPhase1Btn = document.getElementById('back-to-phase1-btn');
    const processAiBtn = document.getElementById('process-ai-btn');

    // Inputs
    const distilledTextInput = document.getElementById('distilled-text-input');
    const aiResponseInput = document.getElementById('ai-response-input');

    // Indicators
    const step1Ind = document.getElementById('step1-indicator');
    const step2Ind = document.getElementById('step2-indicator');
    const step3Ind = document.getElementById('step3-indicator');

    let activeShape = 'box';
    let lastGeneratedHTML = '';

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
                const response = await fetch(`/magic-prompt/distill?text=${encodeURIComponent(text.substring(0, 2000))}`);
                const data = await response.json();

                if (phase1PromptText) {
                    phase1PromptText.textContent = data.prompt;
                    // Reset modal state
                    showPhase(1);
                    magicPromptModal.style.display = 'flex';
                } else {
                    // Fallback if index.html is old
                    const oldOutput = document.getElementById('magic-prompt-text');
                    if (oldOutput) {
                        oldOutput.textContent = data.prompt;
                        magicPromptModal.style.display = 'flex';
                    } else {
                        alert("UI Mismatch: Please hard-reload the page (Ctrl+F5).");
                    }
                }
            } catch (err) {
                console.error('Phase 1 error:', err);
                alert('Failed to generate Phase 1 prompt.');
            } finally {
                magicPromptBtn.disabled = false;
            }
        });
    }

    function showPhase(phase) {
        if (phase === 1) {
            phase1Container.style.display = 'block';
            phase2Container.style.display = 'none';
            step1Ind.className = 'step active';
            step2Ind.className = 'step';
            step3Ind.className = 'step';
        } else if (phase === 2) {
            phase1Container.style.display = 'none';
            phase2Container.style.display = 'block';
            step1Ind.className = 'step completed';
            step2Ind.className = 'step active';
            step3Ind.className = 'step';
        }
    }

    gotoPhase2Btn.addEventListener('click', async () => {
        const distilled = distilledTextInput.value.trim();
        if (!distilled) {
            distilledTextInput.focus();
            return;
        }

        gotoPhase2Btn.disabled = true;
        gotoPhase2Btn.textContent = 'Generating Phase 2...';

        try {
            const response = await fetch(`/magic-prompt/map?distilled_text=${encodeURIComponent(distilled.substring(0, 2000))}`);
            const data = await response.json();
            phase2PromptText.textContent = data.prompt;
            showPhase(2);
        } catch (err) {
            console.error('Phase 2 error:', err);
            alert('Failed to generate Phase 2 prompt.');
        } finally {
            gotoPhase2Btn.disabled = false;
            gotoPhase2Btn.textContent = 'Next: Semantic Mapping';
        }
    });

    backToPhase1Btn.addEventListener('click', () => showPhase(1));

    magicModalCloseBtn.addEventListener('click', () => {
        magicPromptModal.style.display = 'none';
    });

    copyPhase1Btn.addEventListener('click', () => {
        navigator.clipboard.writeText(phase1PromptText.textContent).then(() => {
            copyPhase1Btn.textContent = 'Copied!';
            setTimeout(() => { copyPhase1Btn.textContent = 'Copy Prompt'; }, 2000);
        });
    });

    copyPhase2Btn.addEventListener('click', () => {
        navigator.clipboard.writeText(phase2PromptText.textContent).then(() => {
            copyPhase2Btn.textContent = 'Copied!';
            setTimeout(() => { copyPhase2Btn.textContent = 'Copy Prompt'; }, 2000);
        });
    });

    processAiBtn.onclick = async () => {
        const json = aiResponseInput.value.trim();
        if (!json) {
            aiResponseInput.focus();
            return;
        }

        processAiBtn.disabled = true;
        processAiBtn.textContent = '... Building ...';
        step2Ind.className = 'step completed';
        step3Ind.className = 'step active';

        try {
            const formData = new FormData();
            formData.append('data', json);

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

            lastGeneratedHTML = html;
            downloadBtn.disabled = false;
            downloadMdBtn.disabled = false;
            copyBtn.disabled = false;
            magicPromptModal.style.display = 'none';
            aiResponseInput.value = '';
            distilledTextInput.value = '';
        } catch (err) {
            console.error('Magic render error:', err);
            alert('Failed to render AI response. Ensure it is valid JSON.');
            step3Ind.className = 'step';
            step2Ind.className = 'step active';
        } finally {
            processAiBtn.disabled = false;
            processAiBtn.textContent = 'Build Visual Explanation';
        }
    };

    // ── Shape Button Selection ──
    shapeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            shapeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeShape = btn.dataset.shape;

            // Update placeholder based on shape type
            const placeholders = {
                box: 'Enter text for the box...',
                titled_box: 'Title | Body text here',
                banner: 'Enter banner text...',
                flowchart: 'Step 1 → Step 2 → Step 3',
                table: 'Col1,Col2,Col3|Row1A,Row1B,Row1C|Row2A,Row2B,Row2C',
                callout: 'Enter callout text...',
                pyramid: '5 (height, or: Critical, Important, Optional)',
                separator: 'Section Title',
                vertical_flow: 'Step 1 → Step 2 → Step 3',
            };
            shapeTextInput.placeholder = placeholders[activeShape] || 'Enter text...';
        });
    });

    // Default: first shape button active
    if (shapeButtons.length > 0) {
        shapeButtons[0].classList.add('active');
    }

    // ── Generate Shape ──
    generateShapeBtn.addEventListener('click', async () => {
        const text = shapeTextInput.value.trim();
        if (!text) {
            shapeTextInput.focus();
            return;
        }

        generateShapeBtn.disabled = true;
        generateShapeBtn.textContent = '...';

        try {
            const formData = new FormData();
            formData.append('text', text);
            formData.append('shape', activeShape);
            formData.append('style', shapeStyleSelect.value);
            formData.append('font', 'slant');

            const response = await fetch('/shape-it', { method: 'POST', body: formData });
            const data = await response.json();

            // Show in modal
            shapePreviewOutput.textContent = data.ascii;
            shapeModal.style.display = 'flex';
        } catch (err) {
            console.error('Shape generation error:', err);
            alert('Failed to generate shape. Is the server running?');
        } finally {
            generateShapeBtn.disabled = false;
            generateShapeBtn.textContent = 'Generate';
        }
    });

    // ── Quick Add Shape (Directly to Document) ──
    if (quickAddShapeBtn) {
        quickAddShapeBtn.addEventListener('click', async () => {
            const text = shapeTextInput.value.trim();
            if (!text) {
                shapeTextInput.focus();
                return;
            }

            quickAddShapeBtn.disabled = true;
            quickAddShapeBtn.textContent = '...';

            try {
                const formData = new FormData();
                formData.append('text', text);
                formData.append('shape', activeShape);
                formData.append('style', shapeStyleSelect.value);
                formData.append('font', 'slant');

                const response = await fetch('/shape-it', { method: 'POST', body: formData });
                const data = await response.json();

                // Append directly to textInput
                const ascii = data.ascii;
                const cursorPos = textInput.selectionStart;
                const before = textInput.value.substring(0, cursorPos);
                const after = textInput.value.substring(cursorPos);
                textInput.value = before + '\n```\n' + ascii + '\n```\n' + after;

                // Highlight the changed area briefly
                textInput.classList.add('flash-glow');
                setTimeout(() => textInput.classList.remove('flash-glow'), 1000);

                // Alert the user where it went
                const message = document.createElement('div');
                message.className = 'toast-notification';
                message.textContent = 'Shape added to Document Input below!';
                document.body.appendChild(message);
                setTimeout(() => document.body.removeChild(message), 3000);

            } catch (err) {
                console.error('Quick Add error:', err);
                alert('Failed to add shape.');
            } finally {
                quickAddShapeBtn.disabled = false;
                quickAddShapeBtn.textContent = 'Quick Add ↓';
            }
        });
    }

    // Enter key on shape input
    shapeTextInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            generateShapeBtn.click();
        }
    });

    // ── Modal Controls ──
    modalCloseBtn.addEventListener('click', () => {
        shapeModal.style.display = 'none';
    });

    shapeModal.addEventListener('click', (e) => {
        if (e.target === shapeModal) {
            shapeModal.style.display = 'none';
        }
    });

    copyShapeBtn.addEventListener('click', () => {
        const text = shapePreviewOutput.textContent;
        navigator.clipboard.writeText(text).then(() => {
            copyShapeBtn.textContent = '✓ Copied!';
            setTimeout(() => { copyShapeBtn.textContent = 'Copy ASCII'; }, 2000);
        });
    });

    insertShapeBtn.addEventListener('click', () => {
        const ascii = shapePreviewOutput.textContent;
        const cursorPos = textInput.selectionStart;
        const before = textInput.value.substring(0, cursorPos);
        const after = textInput.value.substring(cursorPos);
        textInput.value = before + '\n```\n' + ascii + '\n```\n' + after;
        shapeModal.style.display = 'none';
        textInput.focus();
    });

    // ── Icon Search ──
    iconSearchBtn.addEventListener('click', async () => {
        const word = iconSearchInput.value.trim();
        if (!word) {
            iconSearchInput.focus();
            return;
        }

        try {
            const response = await fetch(`/lookup/${encodeURIComponent(word)}`);
            const results = await response.json();

            iconSearchResult.innerHTML = '';

            if (results.type !== 'none') {
                const item = document.createElement('div');
                item.className = 'icon-result-item';
                item.title = 'Click to use this icon in your document';
                item.style.cursor = 'pointer';

                item.innerHTML = `
                    <img src="/${results.path}" alt="${results.keyword}">
                    <div>
                        <div class="icon-label">${results.keyword}</div>
                        <div class="icon-match">${results.match} match · ${results.type}</div>
                    </div>
                `;

                item.addEventListener('click', () => {
                    const cursorPos = textInput.selectionStart;
                    const tag = `[${results.keyword}] `;
                    const before = textInput.value.substring(0, cursorPos);
                    const after = textInput.value.substring(cursorPos);
                    textInput.value = before + tag + after;
                    textInput.focus();

                    item.style.background = 'var(--accent-glow-secondary)';
                    setTimeout(() => item.style.background = '', 500);
                });

                iconSearchResult.appendChild(item);
            } else {
                iconSearchResult.innerHTML = `<span style="color: var(--text-muted); font-size: 0.8rem;">No icon found for "${word}"</span>`;
            }
        } catch (err) {
            console.error('Icon search error:', err);
        }
    });

    iconSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            iconSearchBtn.click();
        }
    });

    // ── Explain Form ──
    explainForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = textInput.value.trim();
        if (!text) {
            textInput.focus();
            return;
        }

        // Show loading
        outputContent.innerHTML = '<div class="spinner"></div><p style="text-align:center;color:var(--text-muted);">Generating visual explanation...</p>';
        explainBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('text', text);

            const response = await fetch('/explain', { method: 'POST', body: formData });
            const html = await response.text();

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const explanationBody = doc.querySelector('.explanation-wrapper');

            if (explanationBody) {
                outputContent.innerHTML = explanationBody.innerHTML;
            } else {
                outputContent.innerHTML = html;
            }

            lastGeneratedHTML = html;
            downloadBtn.disabled = false;
            downloadMdBtn.disabled = false;
            copyBtn.disabled = false;

        } catch (err) {
            console.error('Explain error:', err);
            outputContent.innerHTML = `<p style="color: var(--accent-tertiary);">Error generating explanation. Is the server running?</p>`;
        } finally {
            explainBtn.disabled = false;
        }
    });

    // ── Clear Button ──
    clearBtn.addEventListener('click', () => {
        textInput.value = '';
        outputContent.innerHTML = `
                < div class="output-placeholder" >
                    <img src="/openmoji-72x72-color/1F3A8.png" alt="art" width="72" height="72" class="placeholder-emoji">
                        <p>Your visual explanation will appear here</p>
                        <p class="placeholder-sub">Paste text on the left and click "Explain Visually"</p>
                    </div>
            `;
        downloadBtn.disabled = true;
        downloadMdBtn.disabled = true;
        copyBtn.disabled = true;
        lastGeneratedHTML = '';
        textInput.focus();
    });

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
            .replace(/src="\//g, `src = "${origin}/`)
            .replace(/href="\//g, `href="${origin}/`);

        // Ensure UTF-8 meta is present and clean
        if (!standaloneHTML.includes('<meta charset="UTF-8">')) {
            standaloneHTML = standaloneHTML.replace('<head>', '<head><meta charset="UTF-8">');
        }

        downloadFile(standaloneHTML, 'visual-explanation.html', 'text/html;charset=utf-8');
    });

    // ── Download Markdown ──
    downloadMdBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) return;

        downloadMdBtn.disabled = true;
        const originalText = downloadMdBtn.innerHTML;
        downloadMdBtn.innerHTML = '<span class="spinner-sm"></span>';

        try {
            const formData = new FormData();
            formData.append('text', text);

            const response = await fetch('/export-md', { method: 'POST', body: formData });
            const data = await response.json();

            downloadFile(data.markdown, 'explanation.md', 'text/markdown;charset=utf-8');
        } catch (err) {
            console.error('Markdown export error:', err);
            alert('Failed to export Markdown.');
        } finally {
            downloadMdBtn.disabled = false;
            downloadMdBtn.innerHTML = originalText;
        }
    });

    // ── Copy Output ──
    copyBtn.addEventListener('click', () => {
        const text = outputContent.innerText;
        navigator.clipboard.writeText(text).then(() => {
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<img src="/heroicons_24x24/check.svg" alt="" class="btn-icon"> Copied!';
            setTimeout(() => { copyBtn.innerHTML = originalHTML; }, 2000);
        });
    });

    // ── Keyboard Shortcuts ──
    document.addEventListener('keydown', (e) => {
        // Escape: close modal
        if (e.key === 'Escape' && shapeModal.style.display === 'flex') {
            shapeModal.style.display = 'none';
        }
        // Ctrl+Enter: submit form
        if (e.ctrlKey && e.key === 'Enter' && document.activeElement === textInput) {
            e.preventDefault();
            explainForm.dispatchEvent(new Event('submit'));
        }
    });
});
