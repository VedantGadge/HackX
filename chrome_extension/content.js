/* content.js - Captures YouTube captions and injects the reverse translation overlay */

let captionObserver = null;
let captionPoller = null;        // Fallback periodic checker
let overlayContainer = null;
let videoQueue = [];
let isPlaying = false;
let currentCaption = '';
let lastProcessedCaption = '';  // Track last processed caption to avoid duplicates
let lastProcessedTime = 0;      // Track time of last processing for throttling
let captureEnabled = false;      // Track capture state
let queuedTokens = {};          // Track queued tokens: { token: count }
let processedTokens = new Set(); // Track tokens that have been played
let currentlyPlayingToken = null; // Track token currently playing to avoid re-queue during playback
const recentTokens = new Map();   // token -> lastEnqueueTimestamp (ms)
const RECENT_TOKEN_TTL_MS = 3000; // time window to suppress re-enqueueing same token

let backendUrl = 'https://lamaq-signlink-hackx.hf.space';

// Load backend URL from storage
chrome.storage.sync.get('backendUrl', (result) => {
    if (result.backendUrl) {
        backendUrl = result.backendUrl;
        console.log(`[Intellify] Backend URL loaded: ${backendUrl}`);
    }
});

console.log('✅ Intellify content script loaded');

// Initialize the reverse translation overlay
function initOverlay() {
    if (overlayContainer) return;

    overlayContainer = document.createElement('div');
    overlayContainer.id = 'intellify-reverse-overlay';
    overlayContainer.innerHTML = `
        <style>
            #intellify-reverse-overlay {
                position: fixed;
                bottom: 16px;
                right: 16px;
                width: 320px;
                height: 180px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.6);
                background: #000;
                z-index: 9999;
                border: 1px solid rgba(255,255,255,0.2);
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            #intellify-reverse-overlay.hidden {
                display: none;
            }
            #intellify-video-stage {
                position: relative;
                width: 100%;
                height: 100%;
                border-radius: 12px;
                overflow: hidden;
            }
            #intellify-reverse-video {
                width: 100%;
                height: 100%;
                background: #000;
                display: block;
            }
            #intellify-caption {
                position: absolute;
                left: 0;
                right: 0;
                bottom: 0;
                padding: 8px 10px;
                background: linear-gradient(to top, rgba(0,0,0,0.85), rgba(0,0,0,0.0));
                color: #fff;
                font-size: 12px;
                line-height: 1.3;
                font-weight: 600;
                text-align: center;
                word-break: break-word;
                max-height: 60px;
                overflow: hidden;
            }
            #intellify-controls {
                position: absolute;
                top: 4px;
                right: 4px;
                display: flex;
                gap: 4px;
            }
            .intellify-btn {
                background: rgba(0, 0, 0, 0.6);
                border: 1px solid rgba(255,255,255,0.3);
                color: #fff;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .intellify-btn:hover {
                background: rgba(0, 0, 0, 0.8);
                border-color: rgba(255,255,255,0.6);
            }
            .intellify-btn.enabled {
                background: #2563eb;
                border-color: #1d4ed8;
            }
        </style>
        <div id="intellify-video-stage">
            <video id="intellify-reverse-video" muted playsinline></video>
            <div id="intellify-caption">Waiting for captions…</div>
            <div id="intellify-controls">
                <button class="intellify-btn" id="intellify-toggle-btn" title="Toggle sync">Toggle</button>
                <button class="intellify-btn" id="intellify-clear-btn" title="Clear queue">Clear</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlayContainer);

    const toggleBtn = document.getElementById('intellify-toggle-btn');
    const clearBtn = document.getElementById('intellify-clear-btn');
    toggleBtn.addEventListener('click', () => toggleCaptureCaptions());
    clearBtn.addEventListener('click', () => clearQueue());

    console.log('✅ Overlay initialized');
}

// Start capturing captions from YouTube
function startCaptureCaptions() {
    console.log('🎬 Starting caption capture...');
    
    // Try multiple selectors for modern YouTube DOM
    const selectors = [
        '.captions-text',           // Old/Legacy YouTube
        '.ytp-caption-segment',     // Modern YouTube captions
        '.ytp-caption',             // Alternative modern selector
        '[aria-label*="caption"]',  // Accessible elements
        '.a-text[jsname]'           // Google's JavaScript framework
    ];
    
    let captionContainers = [];
    let activeSelector = null;
    
    for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        console.log(`� Trying selector "${selector}": found ${elements.length} element(s)`);
        if (elements.length > 0) {
            captionContainers = elements;
            activeSelector = selector;
            console.log(`✅ Using selector: ${selector}`);
            break;
        }
    }
    
    if (captionContainers.length === 0) {
        console.warn('⚠️ No caption containers found with primary selectors');
        console.warn('🔍 Setting up fallback polling method...');
        
        // If no containers found, use polling as fallback
        if (captionPoller) clearInterval(captionPoller);
        
        // Show persistent notification
        const checkInterval = setInterval(() => {
            // Keep checking if captions are enabled while we wait
            if (!captureEnabled) {
                clearInterval(checkInterval);
                return;
            }
            
            const testElements = Array.from(document.querySelectorAll('.ytp-caption-segment, .captions-text, [aria-label*="caption"]'));
            if (testElements.length > 0) {
                clearInterval(checkInterval);
                console.log('✅ Captions detected! Switching to observer mode...');
                // Restart capture to use observer instead of polling
                stopCaptureCaptions();
                startCaptureCaptions();
                return;
            }
        }, 1000);
        
        captionPoller = setInterval(() => {
            if (!captureEnabled) return;
            
            const captionText = extractCaptionText();
            if (captionText && captionText !== currentCaption) {
                currentCaption = captionText;
                console.log('📝 New caption detected (via polling):', currentCaption);
                processCaption(currentCaption);
            }
        }, 500); // Check every 500ms
        
        console.warn('');
        console.warn('═══════════════════════════════════════════════════════════');
        console.warn('❌ CAPTIONS NOT VISIBLE ON THIS VIDEO');
        console.warn('═══════════════════════════════════════════════════════════');
        console.warn('');
        console.warn('👉 FIX: Click the "CC" (closed captions) button on YouTube');
        console.warn('   It\'s usually in the bottom-right corner of the video player');
        console.warn('');
        console.warn('⏳ I\'m monitoring for captions... (checking every 500ms)');
        console.warn('   Once you enable CC, I\'ll automatically start capturing');
        console.warn('');
        console.warn('═══════════════════════════════════════════════════════════');
        console.warn('');
        
        return;
    }

    // Create observer to detect caption changes
    captionObserver = new MutationObserver(() => {
        const newCaption = extractCaptionText();
        
        if (newCaption) {
            if (newCaption !== currentCaption) {
                currentCaption = newCaption;
                console.log('📝 New caption detected:', currentCaption);
                processCaption(currentCaption);
            } else {
                console.log('🔄 Caption unchanged (same as before), skipping...');
            }
        } else {
            console.log('⏳ Observer fired but no caption text found');
        }
    });

    captionContainers.forEach((container, index) => {
        console.log(`   📌 Observing container ${index + 1}/${captionContainers.length}`);
        captionObserver.observe(container, { childList: true, subtree: true, characterData: true });
    });

    // Also start polling as backup (less frequent, in case mutation observer misses events)
    if (captionPoller) clearInterval(captionPoller);
    captionPoller = setInterval(() => {
        if (!captureEnabled) return;
        
        const newCaption = extractCaptionText();
        if (newCaption && newCaption !== currentCaption) {
            currentCaption = newCaption;
            console.log('📝 New caption detected (via backup polling):', newCaption);
            processCaption(newCaption);
        }
    }, 1000); // Backup polling every 1 second

    console.log(`✅ Caption capture started - watching for caption changes on "${activeSelector}"\n💡 Backup polling enabled every 1 second`);
}

// Helper function to deduplicate and clean caption text
function deduplicateCaption(text) {
    if (!text) return null;
    
    // Split text into words
    const words = text.split(/\s+/);
    
    // Remove consecutive duplicates
    const deduped = [];
    for (let i = 0; i < words.length; i++) {
        // Skip if same as previous word (case-insensitive)
        if (i > 0 && words[i].toLowerCase() === words[i-1].toLowerCase()) {
            continue;
        }
        deduped.push(words[i]);
    }
    
    return deduped.join(' ').trim();
}

// Extract caption text using multiple methods
function extractCaptionText() {
    // Method 1: Try modern YouTube caption container (most reliable)
    let captionText = Array.from(document.querySelectorAll('.ytp-caption-segment, .captions-text span'))
        .map(el => el.textContent.trim())
        .filter(t => t)
        .join(' ');
    
    if (captionText) {
        return deduplicateCaption(captionText);
    }
    
    // Method 2: Try YTP caption windows
    captionText = Array.from(document.querySelectorAll('.ytp-caption-window-bottom .captions-text'))
        .map(el => el.textContent.trim())
        .filter(t => t)
        .join(' ');
    
    if (captionText) {
        return deduplicateCaption(captionText);
    }
    
    // Method 3: Look for aria-label caption (often shows all text including history)
    // For this selector, we need to be more careful about deduplication
    const player = document.querySelector('.html5-video-player, [data-playertype]');
    if (player) {
        const captionElements = player.querySelectorAll('[aria-label*="caption"]');
        if (captionElements.length > 0) {
            // Get the most recent caption element (usually the last one)
            const mostRecentCaption = captionElements[captionElements.length - 1];
            captionText = mostRecentCaption.textContent.trim();
            
            if (captionText && captionText.length < 500) {
                return deduplicateCaption(captionText);
            }
            
            // Fallback: try all captions
            captionText = Array.from(captionElements)
                .map(el => el.textContent.trim())
                .filter(t => t && t.length < 500)
                .join(' ');
            
            if (captionText) {
                return deduplicateCaption(captionText);
            }
        }
    }
    
    // Method 4: Last resort - look for .a-text elements
    const aElements = document.querySelectorAll('.a-text');
    if (aElements.length > 0) {
        captionText = Array.from(aElements)
            .map(el => el.textContent.trim())
            .filter(t => t && t.length < 500)
            .join(' ');
        
        if (captionText) {
            return deduplicateCaption(captionText);
        }
    }
    
    return null;
}

function stopCaptureCaptions() {
    captureEnabled = false;
    
    if (captionObserver) {
        captionObserver.disconnect();
        captionObserver = null;
    }
    
    if (captionPoller) {
        clearInterval(captionPoller);
        captionPoller = null;
    }
    
    console.log('⛔ Caption capture stopped');
}

function toggleCaptureCaptions() {
    const btn = document.getElementById('intellify-toggle-btn');
    if (captureEnabled) {
        stopCaptureCaptions();
        btn.classList.remove('enabled');
    } else {
        captureEnabled = true;
        startCaptureCaptions();
        btn.classList.add('enabled');
    }
}

// Send caption to backend for tokenization and enqueue clips
async function processCaption(text) {
    if (!text.trim()) {
        console.log('⏭️ Caption is empty, skipping...');
        return;
    }

    // Avoid processing identical captions too quickly (deduplicate)
    const now = Date.now();
    if (text === lastProcessedCaption && (now - lastProcessedTime) < 2000) {
        console.log('🔄 Duplicate caption detected (same as last 2 seconds), skipping...');
        return;
    }
    
    lastProcessedCaption = text;
    lastProcessedTime = now;

    console.log(`\n${'='.repeat(60)}`);
    console.log('🌐 TOKENIZATION REQUEST');
    console.log(`Backend URL: ${backendUrl}`);
    console.log(`Caption text: "${text}"`);
    console.log(`Request time: ${new Date().toLocaleTimeString()}`);
    
    try {
        console.log('📤 Sending to backend...');
        const startTime = performance.now();
        
        const resp = await fetch(`${backendUrl}/tokenize-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        const duration = (performance.now() - startTime).toFixed(0);
        console.log(`⏱️ Response time: ${duration}ms`);
        console.log(`📊 Response status: ${resp.status} ${resp.statusText}`);

        if (!resp.ok) {
            console.error(`❌ TOKENIZATION FAILED - HTTP ${resp.status}`);
            console.error(`Status Text: ${resp.statusText}`);
            console.error(`Response: ${await resp.text()}`);
            console.log(`${'='.repeat(60)}\n`);
            return;
        }

        const data = await resp.json();
        console.log('✅ TOKENIZATION SUCCESS');
        console.log(`   Mapped tokens: [${data.tokens?.join(', ') || 'none'}]`);
        console.log(`   All tokens: [${data.tokens_all?.join(', ') || 'none'}]`);
        console.log(`   Missing (no video): [${data.missing?.join(', ') || 'none'}]`);
        console.log(`   Available in videos/: ${data.available?.length || 0} tokens`);

        // Enqueue the mapped tokens with batch pre-fetching
        if (Array.isArray(data.tokens) && data.tokens.length > 0) {
            console.log('🚀 Batch pre-fetching videos...');
            await enqueueTokensBatch(data.tokens);
        } else {
            console.warn('⚠️ No tokens could be mapped to available videos');
        }

        console.log(`${'='.repeat(60)}\n`);

    } catch (e) {
        console.error(`❌ NETWORK ERROR`);
        console.error(`Error type: ${e.name}`);
        console.error(`Error message: ${e.message}`);
        console.error(`Attempted URL: ${backendUrl}/tokenize-text`);
        console.error(`${'='.repeat(60)}\n`);
    }
}

// Batch pre-fetch videos for all tokens (optimized)
async function enqueueTokensBatch(tokens) {
    const now = Date.now();
    
    // Filter tokens that haven't been processed or queued recently
    const tokensToFetch = tokens.filter(token => {
        const tokenLower = String(token).toLowerCase();
        
        // Skip if already processed
        if (processedTokens.has(tokenLower)) {
            console.log(`⏭️ Token "${tokenLower}" already played, skipping...`);
            return false;
        }
        
        // Skip if currently playing
        if (currentlyPlayingToken && tokenLower === currentlyPlayingToken) {
            return false;
        }
        
        // Skip if seen recently
        const lastTs = recentTokens.get(tokenLower);
        if (lastTs && (now - lastTs) < RECENT_TOKEN_TTL_MS) {
            console.log(`⏭️ Token "${tokenLower}" seen recently, skipping...`);
            return false;
        }
        
        // Skip if already in queue
        const isInQueue = videoQueue.some(item => item.token === tokenLower);
        if (isInQueue) {
            console.log(`⏭️ Token "${tokenLower}" already queued, skipping...`);
            return false;
        }
        
        return true;
    });
    
    if (tokensToFetch.length === 0) {
        console.log('⏭️ All tokens already processed/queued, skipping batch fetch');
        return;
    }
    
    try {
        console.log(`📦 Batch fetching ${tokensToFetch.length} videos...`);
        const batchStart = performance.now();
        
        // Batch API call to pre-cache videos on backend
        const resp = await fetch(`${backendUrl}/batch-token-videos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tokens: tokensToFetch })
        });
        
        const batchDuration = (performance.now() - batchStart).toFixed(0);
        
        if (!resp.ok) {
            console.error(`❌ Batch fetch failed, falling back to individual fetch`);
            // Fallback to old method
            enqueueTokens(tokensToFetch);
            return;
        }
        
        const data = await resp.json();
        console.log(`✅ Batch complete in ${batchDuration}ms`);
        
        // Add available videos to queue
        let addedCount = 0;
        for (const token of tokensToFetch) {
            const tokenLower = String(token).toLowerCase();
            const videoUrl = data.videos?.[token];
            
            if (videoUrl) {
                videoQueue.push({ 
                    token: tokenLower, 
                    url: `${backendUrl}${videoUrl}` 
                });
                queuedTokens[tokenLower] = (queuedTokens[tokenLower] || 0) + 1;
                recentTokens.set(tokenLower, now);
                addedCount++;
                console.log(`✅ Added "${tokenLower}" to queue (pre-cached)`);
            } else {
                console.log(`⚠️ No video available for "${tokenLower}"`);
            }
        }
        
        console.log(`📊 Batch Summary: ${addedCount}/${tokensToFetch.length} videos queued`);
        updateCaption();
        playNextFromQueue();
        
    } catch (e) {
        console.error(`❌ Batch fetch error: ${e.message}`);
        // Fallback to old method
        enqueueTokens(tokensToFetch);
    }
}

// Add tokens to the queue (fallback method)
function enqueueTokens(tokens) {
    let addedCount = 0;
    let skippedCount = 0;
    const now = Date.now();
    // Cleanup old entries from recentTokens
    for (const [tok, ts] of recentTokens.entries()) {
        if (now - ts > RECENT_TOKEN_TTL_MS) recentTokens.delete(tok);
    }
    
    tokens.forEach(token => {
        const tokenLower = String(token).toLowerCase();
        
        // Check if token has already been processed
        if (processedTokens.has(tokenLower)) {
            console.log(`⏭️ Token "${tokenLower}" already played, skipping...`);
            skippedCount++;
            return;
        }
        // Suppress if same as currently playing
        if (currentlyPlayingToken && tokenLower === currentlyPlayingToken) {
            console.log(`⏭️ Token "${tokenLower}" is currently playing, skipping...`);
            skippedCount++;
            return;
        }
        // Suppress rapid re-enqueue within TTL window
        const lastTs = recentTokens.get(tokenLower);
        if (lastTs && (now - lastTs) < RECENT_TOKEN_TTL_MS) {
            console.log(`⏭️ Token "${tokenLower}" seen ${now - lastTs}ms ago, within ${RECENT_TOKEN_TTL_MS}ms window — skipping...`);
            skippedCount++;
            return;
        }
        
        // Check if token is already in queue
        const isInQueue = videoQueue.some(item => item.token === tokenLower);
        if (isInQueue) {
            console.log(`⏭️ Token "${tokenLower}" already queued, skipping duplicate...`);
            skippedCount++;
            return;
        }
        
        // Add new token to queue
        videoQueue.push({ 
            token: tokenLower, 
            url: `${backendUrl}/token-video/${encodeURIComponent(token)}` 
        });
        queuedTokens[tokenLower] = (queuedTokens[tokenLower] || 0) + 1;
        recentTokens.set(tokenLower, now);
        addedCount++;
        console.log(`✅ Added "${tokenLower}" to queue`);
    });
    
    console.log(`📊 Enqueue Summary:`);
    console.log(`   Added: ${addedCount} token(s)`);
    console.log(`   Skipped: ${skippedCount} duplicate(s)`);
    console.log(`   Queue total: ${videoQueue.length} item(s)`);
    console.log(`   Processed tokens: ${processedTokens.size}`);
    updateCaption();
    playNextFromQueue();
}

// Play the next video clip from the queue
function playNextFromQueue() {
    if (isPlaying) {
        console.log('⏸️ Already playing, waiting for current video to finish...');
        return;
    }
    
    if (!videoQueue.length) {
        console.log('✅ Queue empty - all videos played!');
        return;
    }

    const next = videoQueue.shift();
    if (!next) {
        console.log('⚠️ Queue item is null/undefined');
        return;
    }

    isPlaying = true;
    const video = document.getElementById('intellify-reverse-video');
    if (!video) {
        console.error('❌ Video element not found!');
        isPlaying = false;
        return;
    }

    console.log(`\n▶️ PLAYING VIDEO CLIP`);
    console.log(`Token: ${next.token}`);
    console.log(`URL: ${next.url}`);
    console.log(`Queue remaining: ${videoQueue.length}`);

    video.src = next.url;
    video.load();
    currentlyPlayingToken = next.token;
    
    const playPromise = video.play();
    if (playPromise !== undefined) {
        playPromise.catch(e => {
            console.error(`❌ Play error for token "${next.token}":`, e.message);
            // Mark as processed even on error to prevent infinite loops
            processedTokens.add(next.token);
            console.log(`✅ Marked "${next.token}" as processed (after error)`);
            isPlaying = false;
            currentlyPlayingToken = null;
            playNextFromQueue();
        });
    }

    // On video end, play next
    const onEnded = () => {
        console.log(`✅ Finished playing: ${next.token}`);
        // Mark this token as processed so it won't be requeued
        processedTokens.add(next.token);
        console.log(`✅ Marked "${next.token}" as processed (played successfully)`);
        console.log(`   Total processed: ${processedTokens.size}`);
        isPlaying = false;
        currentlyPlayingToken = null;
        video.removeEventListener('ended', onEnded);
        updateCaption();
        playNextFromQueue();
    };
    video.addEventListener('ended', onEnded);

    console.log(`⏱️ Video loaded and playing\n`);
    updateCaption();
}

// Update the caption overlay with current and next tokens
function updateCaption() {
    const captionEl = document.getElementById('intellify-caption');
    if (!captionEl) return;

    const nextTokens = videoQueue.slice(0, 3).map(x => x.token.toUpperCase());
    if (nextTokens.length === 0) {
        captionEl.textContent = 'Waiting for captions…';
    } else {
        captionEl.textContent = `Next: ${nextTokens.join(' · ')}`;
    }
}

// Clear the queue
function clearQueue() {
    videoQueue = [];
    queuedTokens = {};
    processedTokens.clear();
    currentlyPlayingToken = null;
    recentTokens.clear();
    isPlaying = false;
    const video = document.getElementById('intellify-reverse-video');
    if (video) {
        video.pause();
        video.removeAttribute('src');
        video.load();
    }
    updateCaption();
    console.log('🧹 Queue cleared - reset all tracking');
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'toggleCaptions') {
        const isEnabled = !captionObserver;
        if (isEnabled) {
            startCaptureCaptions();
            console.log('🎯 Caption capture started from popup');
        } else {
            stopCaptureCaptions();
            console.log('⏹️ Caption capture stopped from popup');
        }
        sendResponse({ success: true, enabled: isEnabled });
    } else if (request.action === 'clearQueue') {
        clearQueue();
        sendResponse({ success: true });
    }
});

// Initialize on load
window.addEventListener('load', () => {
    initOverlay();
    console.log('✅ Intellify ready on youtube.com');
});
