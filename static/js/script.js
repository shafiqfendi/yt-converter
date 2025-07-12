document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('converter-form');
    const urlInput = document.getElementById('youtube-url');
    const convertBtn = document.getElementById('convert-btn');
    const messageArea = document.getElementById('message-area');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const youtubeURL = urlInput.value.trim();
        if (!youtubeURL) {
            showMessage('Please enter a YouTube URL.', 'error');
            return;
        }

        convertBtn.disabled = true;
        convertBtn.textContent = 'Converting...';
        showMessage('Processing your request, please wait...', 'success');

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: youtubeURL }),
            });

            if (response.ok) {
                const blob = await response.blob();
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'audio.mp3';

                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+?)"/);
                    if (filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }

                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                a.remove();

                showMessage('Conversion successful! Your download has started.', 'success');
            } else {
                const errorData = await response.json();
                showMessage(`Error: ${errorData.error}`, 'error');
            }
        } catch (error) {
            showMessage('An unexpected error occurred. Please check the console.', 'error');
            console.error('Fetch error:', error);
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = 'Convert';
            urlInput.value = '';
        }
    });

    function showMessage(message, type) {
        messageArea.textContent = message;
        messageArea.className = type;
    }
});
