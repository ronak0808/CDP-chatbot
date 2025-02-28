document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const examples = document.querySelectorAll('.examples li');

    // Handle example clicks
    examples.forEach(example => {
        example.addEventListener('click', () => {
            const question = example.textContent.replace(/["]/g, '');
            userInput.value = question;
            userInput.focus();
        });
    });

    // Add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (typeof content === 'string') {
            // Handle newlines and format as paragraphs
            const paragraphs = content.split('\n').filter(p => p.trim());
            paragraphs.forEach((p, index) => {
                const paragraph = document.createElement('p');
                paragraph.textContent = p;
                messageContent.appendChild(paragraph);
                
                // Add spacing between paragraphs
                if (index < paragraphs.length - 1) {
                    messageContent.appendChild(document.createElement('br'));
                }
            });
        } else {
            messageContent.textContent = content;
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Show loading animation
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot';
        loadingDiv.innerHTML = `
            <div class="loading">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return loadingDiv;
    }

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const question = userInput.value.trim();
        if (!question) return;

        // Disable input and button while processing
        const submitButton = chatForm.querySelector('button');
        userInput.disabled = true;
        submitButton.disabled = true;

        // Add user message
        addMessage(question, true);
        
        // Clear input
        userInput.value = '';

        // Show loading animation
        const loadingDiv = showLoading();

        try {
            // Send request to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });

            // Remove loading animation
            loadingDiv.remove();

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            if (data.error) {
                addMessage('Sorry, I encountered an error. Please try again.');
            } else {
                addMessage(data.response);
            }

        } catch (error) {
            // Remove loading animation if still present
            loadingDiv.remove();
            
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error. Please try again.');
        } finally {
            // Re-enable input and button
            userInput.disabled = false;
            submitButton.disabled = false;
            userInput.focus();
        }
    });

    // Handle input changes
    userInput.addEventListener('input', () => {
        const submitButton = chatForm.querySelector('button');
        submitButton.disabled = !userInput.value.trim();
    });

    // Handle Enter key
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Focus input on page load
    userInput.focus();
});
