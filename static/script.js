/* ═══════════════════════════════════════════════════════════
   TextPrism Project — Frontend Logic (script.js)
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM Elements ──
    const textInput = document.getElementById('text-input');
    const clearBtn = document.getElementById('clear-btn');
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
    const aiResponseInput = document.getElementById('ai-response-input');
    const processAiBtn = document.getElementById('process-ai-btn');
    const magicModalCloseBtn = document.getElementById('magic-modal-close');

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
                const response = await fetch('/magic-prompt/unified', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
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
        outputContent.innerHTML = `
                <div class="output-placeholder">
                    <img src="/icons/openmoji/1F3B8.png" alt="art" width="72" height="72" class="placeholder-emoji">
                            <p>Your visual explanation will appear here</p>
                        <p class="placeholder-sub">Paste text on the left and click "Explain & Map with AI"</p>
                    </div>
            `;
        downloadBtn.disabled = true;
        if (downloadPdfBtn) downloadPdfBtn.disabled = true;
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
            .replace(/src="\//g, `src="${origin}/`)
            .replace(/href="\//g, `href="${origin}/`);

        // Ensure UTF-8 meta is present and clean
        if (!standaloneHTML.includes('<meta charset="UTF-8">')) {
            standaloneHTML = standaloneHTML.replace('<head>', '<head><meta charset="UTF-8">');
        }

        downloadFile(standaloneHTML, 'visual-explanation.html', 'text/html;charset=utf-8');
    });

    // ── Download PDF ──
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => {
            const element = outputContent;
            if (!element || !element.innerHTML.trim() || element.querySelector('.output-placeholder')) {
                alert('No content to export as PDF.');
                return;
            }

            const options = {
                margin: [10, 10, 10, 10],
                filename: 'TextPrism_Explanation.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: {
                    scale: 2,
                    useCORS: true,
                    letterRendering: true,
                    backgroundColor: window.getComputedStyle(document.documentElement).getPropertyValue('--bg-primary').trim() || '#f8fafc'
                },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
                pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
            };

            const originalHTML = downloadPdfBtn.innerHTML;
            downloadPdfBtn.disabled = true;
            downloadPdfBtn.innerHTML = '<span class="spinner-sm"></span>';

            const images = element.querySelectorAll('img');
            const promises = Array.from(images).map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(resolve => {
                    img.onload = resolve;
                    img.onerror = resolve;
                });
            });

            Promise.all(promises).then(() => {
                if (typeof html2pdf === 'undefined') {
                    throw new Error('html2pdf library not loaded.');
                }

                return html2pdf().set(options).from(element).save();
            }).catch(err => {
                console.error('PDF Export Critical error:', err);
                alert(`Failed to export PDF: ${err.message}`);
            }).finally(() => {
                downloadPdfBtn.disabled = false;
                downloadPdfBtn.innerHTML = originalHTML;
            });
        });
    }

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
