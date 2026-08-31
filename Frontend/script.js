const ws = new WebSocket("ws://localhost:9000/ws");
const landingView = document.getElementById("landing-view");
const dashboardView = document.getElementById("dashboard-view");
const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("messageInput");
const continuousBtn = document.getElementById("continuousBtn");
const statusBar = document.getElementById("status-bar");

let isDashboardActive = false;
let isContinuousActive = false;
let manualStop = false;
let isAiSpeaking = false;
let restartTimeout = null;

function transitionToDashboard(initialText = "") {
    if (isDashboardActive) return;
    isDashboardActive = true;

    landingView.classList.add("hidden");
    dashboardView.classList.add("visible");

    setTimeout(() => {
        if (initialText) {
            messageInput.value = initialText;
            sendMessage();
        }
        if (!isContinuousActive) {
            toggleContinuousMode();
        }
    }, 600);
}

window.addEventListener('mousemove', () => {
    transitionToDashboard();
}, { once: true });

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'fr-FR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognition.onstart = function() {
        statusBar.textContent = "State: 🎤 Listening...";
    };

    recognition.onresult = function(event) {
        if (isAiSpeaking) return;
        const speechText = event.results[0][0].transcript.trim();
        console.log("🗣️ Texte capté :", speechText);

        if (!isDashboardActive) {
            transitionToDashboard(speechText);
        } else {
            messageInput.value = speechText;
            sendMessage();
        }
    };

    recognition.onerror = function(event) {
        if (event.error === 'aborted' || event.error === 'no-speech') return;
        statusBar.textContent = `State: Microphone error (${event.error})`;
    };

    recognition.onend = function() {
        if (isContinuousActive && !manualStop && !isAiSpeaking) {
            statusBar.textContent = "State: 🔄 Resetting sensor...";
            clearTimeout(restartTimeout);
            restartTimeout = setTimeout(() => {
                if (isContinuousActive && !manualStop && !isAiSpeaking) {
                    try {
                        recognition.start();
                    } catch (e) {}
                }
            }, 400);
        } else if (!isContinuousActive) {
            statusBar.textContent = "State: Waiting";
        }
    };

    try {
        recognition.start();
        isContinuousActive = true;
    } catch (e) {
        console.log("Start the microphone.");
    }
}

function toggleContinuousMode() {
    if (!recognition) return;

    isContinuousActive = !isContinuousActive;
    if (isContinuousActive) {
        manualStop = false;
        continuousBtn.classList.add("active");
        continuousBtn.textContent = "🛑 Stop listening";
        try { recognition.start(); } catch (e) {}
    } else {
        manualStop = true;
        continuousBtn.classList.remove("active");
        continuousBtn.textContent = "🎙️ Mode Continu";
        statusBar.textContent = "State: Manually stopped";
        try { recognition.stop(); } catch(e) {}
    }
}

ws.onopen = function() {
    console.log("Connecté au WebSocket du backend.");
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    chatBox.innerHTML += `<div class="message user"><b>Moi :</b> ${data.user_message}</div>`;
    chatBox.innerHTML += `<div class="message ai"><b>IA :</b> ${data.ai_message}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    speakText(data.ai_message);
};

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'fr-FR';
        utterance.rate = 1.0;
        
        utterance.onstart = function() {
            isAiSpeaking = true;
            statusBar.textContent = "State: 🤖 Voice synthesis active...";
            if (recognition) {
                try { recognition.stop(); } catch(e) {}
            }
        };

        utterance.onend = function() {
            isAiSpeaking = false;
            if (isContinuousActive && !manualStop && recognition) {
                setTimeout(() => {
                    try { recognition.start(); } catch(e) {}
                }, 500);
            } else {
                statusBar.textContent = "State: Waiting";
            }
        };

        window.speechSynthesis.speak(utterance);
    }
}

function sendMessage() {
    const text = messageInput.value.trim();
    if (text) {
        ws.send(text);
        messageInput.value = "";
    }
}

function checkEnter(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}