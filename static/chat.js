document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chatHistory');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    let history = []; // Store conversation history

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message message-${role}`;

        const avatar = role === 'ai' ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';

        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="bubble">${formatText(text)}</div>
        `;

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function formatText(text) {
        // Simple formatting for newlines and bold
        return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'message message-ai';
        typingDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="bubble typing">
                <span></span><span></span><span></span>
            </div>
        `;
        chatHistory.appendChild(typingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function removeTyping() {
        const typingDiv = document.getElementById('typingIndicator');
        if (typingDiv) typingDiv.remove();
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message
        appendMessage('user', message);
        userInput.value = '';

        // Add to history
        history.push({ role: 'user', content: message });

        // Show typing
        showTyping();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    history: history
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();

            removeTyping();
            appendMessage('ai', data.response);

            // Add AI response to history
            history.push({ role: 'model', content: data.response });

        } catch (error) {
            console.error('Error:', error);
            removeTyping();
            appendMessage('ai', 'Maaf, terjadi kesalahan koneksi. Silakan coba lagi.');
        }
    });
});
