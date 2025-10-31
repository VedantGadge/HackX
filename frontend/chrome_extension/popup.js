/* popup.js - Handles the extension popup UI */

document.getElementById('toggleBtn').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'toggleCaptions' });
    });
});

document.getElementById('clearBtn').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'clearQueue' });
    });
});

// Update backend URL
document.getElementById('backendUrl').addEventListener('change', (e) => {
    chrome.storage.sync.set({ backendUrl: e.target.value });
});

// Load saved backend URL
chrome.storage.sync.get('backendUrl', (result) => {
    if (result.backendUrl) {
        document.getElementById('backendUrl').value = result.backendUrl;
    }
});
