/* ═══════════════════════════════════════════════════════════
   TextPrism Project — Frontend Logic (script.js)
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM Elements ──
    const textInput = document.getElementById('text-input');
    const clearBtn = document.getElementById('clear-btn');
    const outputContent = document.getElementById('output-content');
    const downloadBtn = document.getElementById('download-html-btn');
    const downloadMdBtn = document.getElementById('download-md-btn');
    const copyBtn = document.getElementById('copy-btn');




    // Modal


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

    /* AI Tier Selection removed */

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
                const response = await fetch('/magic-prompt/distill', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
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
            const response = await fetch('/magic-prompt/map', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ distilled_text: distilled })
            });
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
        const textToCopy = phase1PromptText.innerText || phase1PromptText.textContent;
        navigator.clipboard.writeText(textToCopy).then(() => {
            copyPhase1Btn.textContent = 'Copied!';
            copyPhase1Btn.classList.add('btn-accent');
            setTimeout(() => {
                copyPhase1Btn.textContent = 'Copy Prompt';
                copyPhase1Btn.classList.remove('btn-accent');
            }, 2000);
        });
    });

    copyPhase2Btn.addEventListener('click', () => {
        const textToCopy = phase2PromptText.innerText || phase2PromptText.textContent;
        navigator.clipboard.writeText(textToCopy).then(() => {
            copyPhase2Btn.textContent = 'Copied!';
            copyPhase2Btn.classList.add('btn-accent');
            setTimeout(() => {
                copyPhase2Btn.textContent = 'Copy Prompt';
                copyPhase2Btn.classList.remove('btn-accent');
            }, 2000);
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



    /* Explain Form submit handler removed - now using Magic Prompt workflow */

    // ── Clear Button ──
    clearBtn.addEventListener('click', () => {
        textInput.value = '';
        outputContent.innerHTML = `
                <div class="output-placeholder">
                    <img src="/icons/openmoji/1F3B8.png" alt="art" width="72" height="72" class="placeholder-emoji">
                        <p>Your visual explanation will appear here</p>
                        <p class="placeholder-sub">Paste text on the left and click "Summarize & Map with AI"</p>
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
            copyBtn.innerHTML = '<img src="/icons/heroicons/check.svg" alt="" class="btn-icon"> Copied!';
            setTimeout(() => { copyBtn.innerHTML = originalHTML; }, 2000);
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
