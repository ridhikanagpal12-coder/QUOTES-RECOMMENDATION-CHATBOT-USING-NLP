// Configuration
const RASA_SERVER_URL = 'https://quotes-recommendation-chatbot-using-nlp-wzll.onrender.com/webhooks/rest/webhook';
let sessionId = 'user_' + Date.now() + '_' + Math.random().toString(36).substring(7);
let conversationStarted = false;
let currentQuote = '';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Ultimate QuoteBot frontend loaded');
    
    // Set quote count
    document.getElementById('quoteCount').textContent = '100+';
    
    // Focus input
    document.getElementById('userInput').focus();
    
    // Load chat history
    loadChatHistory();
    
    // Attach listeners
    attachEventListeners();
});

function attachEventListeners() {
    // Send button
    document.getElementById('sendButton')?.addEventListener('click', sendUserMessage);
    
    // Enter key
    document.getElementById('userInput')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });
    
    // Clear chat button in header
    const clearBtn = document.querySelector('.header-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearChat);
    }
}

function hideWelcome() {
    if (!conversationStarted) {
        const welcomeScreen = document.getElementById('welcomeScreen');
        const chatMessages = document.getElementById('chatMessages');
        const quickActions = document.getElementById('quickActions');
        const typingIndicator = document.getElementById('typingIndicator');
        
        if (welcomeScreen) welcomeScreen.classList.add('hidden');
        if (chatMessages) chatMessages.classList.remove('hidden');
        if (quickActions) quickActions.classList.remove('hidden');
        if (typingIndicator) typingIndicator.style.display = 'none';
        
        conversationStarted = true;
    }
}

function addMessage(text, isUser = false) {
    hideWelcome();
    
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    // Content
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Format quote if it's a bot message and contains quote markers
    if (!isUser && (text.includes('"') || text.includes('—'))) {
        const parts = text.split('\n\n');
        if (parts.length > 1) {
            content.innerHTML = `<i class="fas fa-quote-left"></i> ${parts[0]}<br><br>`;
            content.innerHTML += parts.slice(1).join('<br><br>');
        } else {
            content.textContent = text;
        }
        
        // Add category tag if present
        if (text.includes('#')) {
            content.innerHTML += '<br><span class="quote-category">' + 
                text.split('#')[1] + '</span>';
        }
    } else {
        content.textContent = text;
    }
    
    // Time
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    content.appendChild(time);
    
    // Assemble
    if (!isUser) {
        messageDiv.appendChild(avatar);
    }
    messageDiv.appendChild(content);
    if (isUser) {
        messageDiv.appendChild(avatar);
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    // Save to localStorage
    saveChatHistory();
    
    // Store quote for feedback
    if (!isUser && text.includes('"')) {
        currentQuote = text;
    }
}

function addTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = 'block';
        scrollToBottom();
    }
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    const chatArea = document.querySelector('.chat-area');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

async function sendToRasa(message) {
    try {
        const response = await fetch(RASA_SERVER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender: sessionId,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`Rasa server error: ${response.status}`);
        }

        const data = await response.json();
        removeTypingIndicator();

        if (data && data.length > 0) {
            data.forEach(msg => {
                if (msg.text) {
                    addMessage(msg.text, false);
                    
                    // Show feedback options for quotes
                    if (msg.text.includes('"') && msg.text.includes('—')) {
                        setTimeout(() => showFeedbackOptions(), 1000);
                    }
                }
            });
        } else {
            addMessage("I'm here to help! Try asking for motivation, love quotes, or tell me how you feel.", false);
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage("⚠️ Cannot connect to Rasa. Make sure it's running on port 5005.\n\nTry: `rasa run --enable-api --cors \"*\"`", false);
    }
}

function sendUserMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (message) {
        sendMessage(message);
        input.value = '';
    }
}

function sendMessage(text) {
    addMessage(text, true);
    addTypingIndicator();
    sendToRasa(text);
}

function sendCategory(category) {
    const messages = {
        'motivation': 'motivate me',
        'success': 'give me a success quote',
        'love': 'love quote',
        'humor': 'tell me a joke',
        'inspiration': 'inspire me',
        'wisdom': 'give me wisdom'
    };
    sendMessage(messages[category] || `I want ${category} quotes`);
}

function sendEmotion(emotion) {
    const messages = {
        'happy': "I'm feeling happy today",
        'sad': "I feel sad",
        'stressed': "I'm stressed",
        'excited': "I'm excited",
        'tired': "I'm tired",
        'anxious': "I feel anxious",
        'lonely': "I feel lonely",
        'romantic': "I'm feeling romantic"
    };
    sendMessage(messages[emotion] || `I feel ${emotion}`);
}

function showFeedbackOptions() {
    // You can implement a feedback modal here
    console.log('Show feedback for quote:', currentQuote);
}

function clearChat() {
    if (confirm('Clear all messages?')) {
        const messagesContainer = document.getElementById('chatMessages');
        const welcomeScreen = document.getElementById('welcomeScreen');
        const quickActions = document.getElementById('quickActions');
        const typingIndicator = document.getElementById('typingIndicator');
        
        if (messagesContainer) messagesContainer.innerHTML = '';
        if (welcomeScreen) welcomeScreen.classList.remove('hidden');
        if (quickActions) quickActions.classList.add('hidden');
        if (typingIndicator) typingIndicator.style.display = 'none';
        
        conversationStarted = false;
        localStorage.removeItem('chatHistory');
        
        // Reset session ID for new conversation
        sessionId = 'user_' + Date.now() + '_' + Math.random().toString(36).substring(7);
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        if (sidebar.style.display === 'none' || getComputedStyle(sidebar).display === 'none') {
            sidebar.style.display = 'block';
        } else {
            sidebar.style.display = 'none';
        }
    }
}

function toggleVoiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        recognition.onstart = function() {
            console.log('Voice recognition started');
            addMessage("🎤 Listening...", false);
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('userInput').value = transcript;
            console.log('Voice input:', transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('Voice error:', event.error);
            addMessage("❌ Couldn't hear you. Please try again or type your message.", false);
        };
        
        recognition.start();
    } else {
        alert('Speech recognition is not supported in this browser. Try Chrome or Edge!');
    }
}

function showEmojis() {
    const emojis = ['😊', '😄', '😍', '🤔', '😢', '😰', '🎉', '💪', '🌟', '❤️', '✨', '🔥', '💯', '🙏'];
    const input = document.getElementById('userInput');
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    
    // Insert at cursor position or append
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;
    
    input.value = text.substring(0, start) + randomEmoji + text.substring(end);
    
    // Move cursor after inserted emoji
    input.selectionStart = input.selectionEnd = start + 2;
    input.focus();
}

function saveChatHistory() {
    const messages = document.getElementById('chatMessages')?.innerHTML;
    if (messages && messages.trim() !== '') {
        localStorage.setItem('chatHistory', messages);
    }
}

function loadChatHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved && saved.trim() !== '') {
        const messagesContainer = document.getElementById('chatMessages');
        const welcomeScreen = document.getElementById('welcomeScreen');
        const quickActions = document.getElementById('quickActions');
        
        if (messagesContainer) {
            messagesContainer.innerHTML = saved;
            messagesContainer.classList.remove('hidden');
            if (welcomeScreen) welcomeScreen.classList.add('hidden');
            if (quickActions) quickActions.classList.remove('hidden');
            conversationStarted = true;
            scrollToBottom();
        }
    }
}

// Make functions global for onclick handlers
window.sendCategory = sendCategory;
window.sendEmotion = sendEmotion;
window.sendMessage = sendMessage;
window.clearChat = clearChat;
window.toggleSidebar = toggleSidebar;
window.toggleVoiceInput = toggleVoiceInput;
window.showEmojis = showEmojis;
window.sendUserMessage = sendUserMessage;

// Handle page visibility
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible again
        document.getElementById('userInput')?.focus();
    }
});
