# Phase 3: Testing & Verification Guide

**Status:** Testing framework created and ready for manual/automated verification

**Completion Date:** October 30, 2025

---

## Overview

Phase 3 focuses on end-to-end integration testing of the real-time classroom system. This document provides both automated test suite setup and manual testing procedures.

---

## Test Artifacts Created

### 1. `test_classroom_integration.py` (387 lines)

**Purpose:** Comprehensive unit and integration test suite

**Test Classes:**

#### ClassroomIntegrationTest
- Route existence tests
- WebSocket connection events (`teacher_join`, `student_join`, `disconnect`)
- Speech processing pipeline (`send_speech` event)
- Multi-client synchronization
- Error handling

#### AudioProcessingTest
- Base64 audio encoding/decoding
- Audio format detection (WAV, WebM)
- Audio duration calculation

#### PerformanceTest
- Single send_speech latency measurement
- Concurrent user load testing (5+ students)
- Memory usage over extended sessions
- Caption broadcast delay

#### MockedAppTest
- Room ID generation and uniqueness
- Video URL construction
- Timestamp formatting

---

## Manual Testing Procedures

### Pre-Test Setup

```bash
# 1. Ensure dependencies installed
pip list | grep -E "flask|socketio|openai"

# 2. Verify .env has OpenAI key
cat .env | grep OPENAI_API_KEY

# 3. Check video library exists
ls videos/ | head -10

# 4. Start the Flask app
python app.py
# Expected: "Running on http://localhost:5000"
```

---

## Test Scenarios

### Scenario 1: Single Student Real-time Translation

**Duration:** 5 minutes

**Steps:**

1. **Open Browser 1 (Teacher)**
   - Navigate to `http://localhost:5000/classroom`
   - Click "Teacher" card
   - Enter name (e.g., "Ms. Johnson")
   - Click "Start Teaching"
   - **Verify:** Room code displayed (e.g., "ABC123"), student count = 0

2. **Open Browser 2 (Student)**
   - Navigate to `http://localhost:5000/classroom`
   - Click "Student" card
   - Enter room code from Browser 1
   - Click "Join Class"
   - **Verify:** Redirects to student.html, connection status "Connected"

3. **Back to Browser 1 (Teacher)**
   - **Verify:** Student count incremented to 1
   - Click "Start Recording"
   - Speak clearly: "Hello everyone, welcome to sign language class"
   - Speak for 3-5 seconds
   - Click "Stop Recording"
   - **Verify:** Captions appear (e.g., "hello everyone welcome to sign language class")
   - **Verify:** Captions added to history

4. **Browser 2 (Student)**
   - **Verify:** Video auto-plays
   - **Verify:** Transcript updates with gloss tokens
   - **Verify:** Stats update (Videos Received: 1, Total Words: ~6)
   - Click "Replay" button
   - **Verify:** Video restarts

5. **Back to Browser 1 (Teacher)**
   - Record another speech: "Very good"
   - **Verify:** Second video broadcasts

6. **Browser 2 (Student)**
   - **Verify:** Second video auto-plays
   - **Verify:** Transcript now shows both entries

**Success Criteria:**
- ✅ Video displays in student browser within 5 seconds of teacher speaking
- ✅ Captions appear in teacher dashboard
- ✅ Transcript syncs in student dashboard
- ✅ Multiple videos handled correctly
- ✅ No console errors in either browser

---

### Scenario 2: Multiple Students Synchronization

**Duration:** 10 minutes

**Steps:**

1. **Browser 1 (Teacher):** Same setup as Scenario 1
2. **Browser 2 (Student 1):** Join room
   - **Verify:** Student count = 1
3. **Browser 3 (Student 2):** Join same room
   - **Verify:** Browser 1 shows count = 2
   - **Verify:** Browser 2 sees no changes (connection already established)
4. **Browser 4 (Student 3):** Join same room
   - **Verify:** Browser 1 shows count = 3
5. **Browser 1 (Teacher):** Speak
   - Record: "Everyone ready? Let's practice the alphabet"
6. **Browsers 2, 3, 4 (All Students):**
   - **Verify:** All three receive identical video simultaneously
   - **Verify:** All three have matching transcripts

**Success Criteria:**
- ✅ All students receive video at same time (±500ms)
- ✅ No individual students receive duplicate or missing videos
- ✅ Student count accurately reflects connections
- ✅ Broadcast latency < 2 seconds per event

---

### Scenario 3: Error Handling

**Duration:** 5 minutes

**Steps:**

1. **Invalid Room Code**
   - Student enters wrong room code (e.g., "XYZ999")
   - **Expected:** Error or "Teacher not found" message

2. **Teacher Ends Session**
   - Teacher clicks "End Session" button
   - **Expected:** Browser 1 redirects to /classroom
   - **Expected:** Browsers 2-4 show "Disconnected" status or disconnect message

3. **Student Leaves Early**
   - Student clicks "Leave Class" button
   - **Expected:** Browser redirects to /classroom
   - **Expected:** Teacher sees student count decrement

4. **Network Interruption (Simulate)**
   - Close one student browser tab
   - **Expected:** Teacher sees student count decrement after 30 seconds
   - **Expected:** No errors in teacher/other student browsers

**Success Criteria:**
- ✅ Graceful handling of invalid inputs
- ✅ Clean disconnection when leaving
- ✅ No uncaught JavaScript errors
- ✅ Stale connections cleaned up

---

### Scenario 4: Content Verification

**Duration:** 3 minutes

**Steps:**

1. Teacher records speech with specific words
   - "The quick brown fox"

2. **Verify Transcription:**
   - Captions show transcribed text accurately
   - Common mistakes (e.g., "th" → "d", accents) noted

3. **Verify Gloss Conversion:**
   - Gloss tokens in transcript match expected sign language glosses
   - Example: "the" (article) may be omitted in ASL gloss

4. **Verify Video Composition:**
   - Check `/outputs/` directory
   - File format: `reverse_YYYYMMDD_HHMMSS_microseconds.mp4`
   - File size > 100KB (indicates actual video)

5. **Verify Video Playback:**
   - Student clicks "Play" button
   - Video plays smoothly without stuttering
   - No audio track present (video only)

**Success Criteria:**
- ✅ Transcription accuracy > 85%
- ✅ Gloss tokens reasonable for sign language
- ✅ Video files generated and playable
- ✅ Smooth playback on Chrome/Firefox/Edge

---

## Automated Testing

### Run Full Test Suite

```bash
python -m pytest test_classroom_integration.py -v

# Or use unittest directly
python -m unittest test_classroom_integration -v
```

### Run Specific Test Class

```bash
python -m unittest test_classroom_integration.ClassroomIntegrationTest -v
python -m unittest test_classroom_integration.AudioProcessingTest -v
```

### Run with Coverage

```bash
pip install coverage
coverage run -m unittest test_classroom_integration
coverage report -m
coverage html  # Generate HTML report
```

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Transcription Latency | 2-3s | < 5s | > 10s ❌ |
| Gloss Conversion | 0.5s | < 1s | > 2s ❌ |
| Video Composition | 1-2s | < 3s | > 5s ❌ |
| Broadcast to Students | 0.2s | < 0.5s | > 1s ❌ |
| **Total E2E Latency** | **3.7s** | **< 8s** | **> 12s ❌** |
| Concurrent Users | 10+ | 5-10 | < 5 ❌ |
| Caption Delivery | < 1s | < 2s | > 3s ❌ |
| Memory per Session | 50MB | < 100MB | > 200MB ❌ |

### Measurement Commands

**Transcription Time:**
```python
import time
start = time.time()
text = transcribe_audio(audio_base64)
print(f"Transcription: {time.time() - start:.2f}s")
```

**End-to-End Time:**
```bash
# Use browser DevTools Console
console.time('send_speech');
socket.emit('send_speech', {...});
socket.on('video_broadcast', () => console.timeEnd('send_speech'));
```

---

## Debugging Checklist

### If videos don't appear in student browsers:

1. ✅ Teacher is actually recording (recording status indicator visible)
2. ✅ Stop Recording button clicked (not still recording)
3. ✅ Browser console shows no errors (F12 → Console tab)
4. ✅ Network tab shows `video_broadcast` event (F12 → Network tab)
5. ✅ Student browser console shows `video_broadcast` received
6. ✅ Video file exists in `/outputs/` directory
7. ✅ OpenAI API key valid (test with: `python test_model_connection.py`)

### If captions don't appear:

1. ✅ Microphone permission granted (check browser URL bar)
2. ✅ Audio actually recorded (waveform shows something, file > 1KB)
3. ✅ OpenAI Whisper API responding
4. ✅ Gloss conversion function working (run `python revtrans.py` with test text)

### If students can't join room:

1. ✅ Room code matches exactly (6-character uppercase)
2. ✅ Teacher still in room (didn't close tab/click End Session)
3. ✅ Same room_id in query parameter
4. ✅ WebSocket connection established (connection status = "Connected")

### If performance is slow:

1. ✅ Check OpenAI API rate limits (Dashboard → Usage)
2. ✅ Monitor network latency (DevTools → Network tab)
3. ✅ Check CPU/memory on server (Resource Monitor)
4. ✅ Reduce video bitrate if needed
5. ✅ Test with fewer concurrent students

---

## Known Issues & Workarounds

### Issue 1: Microphone Permission Denied
**Symptom:** "Could not access microphone" alert appears

**Workaround:**
- Click browser lock icon (URL bar)
- Change Microphone permission to "Allow"
- Refresh page

### Issue 2: CORS Errors in Console
**Symptom:** Cross-Origin error in browser console

**Workaround:**
- Already fixed in `app.py` line 58: `cors_allowed_origins="*"`
- If still occurring, restart Flask app

### Issue 3: Videos Autoplay Not Working
**Symptom:** Video received but doesn't auto-play

**Workaround:**
- Browser privacy setting: Allow autoplay without sound
- In Chrome: Settings → Privacy → Autoplay
- Manually click Play button as fallback

### Issue 4: Transcript Download Fails
**Symptom:** Download button does nothing

**Workaround:**
- Check browser download settings
- Try different browser
- Check for JavaScript errors (F12 → Console)

---

## Test Results Template

```
Date: 2025-10-30
Tester: [Your Name]
Duration: [Total Time]

SCENARIO RESULTS
================

Scenario 1: Single Student
- [ ] Teacher setup successful
- [ ] Student join successful
- [ ] Video broadcast received
- [ ] Captions appear
- [ ] Transcript syncs
Issues: [List any problems]

Scenario 2: Multiple Students
- [ ] All students connect
- [ ] Count increments correctly
- [ ] All receive same video
- [ ] No delays/duplicates
Issues: [List any problems]

Scenario 3: Error Handling
- [ ] Invalid room handled
- [ ] Disconnect works
- [ ] Leave button works
- [ ] No stale connections
Issues: [List any problems]

Scenario 4: Content Verification
- [ ] Transcription accurate
- [ ] Gloss tokens correct
- [ ] Video files generated
- [ ] Video plays smoothly
Issues: [List any problems]

PERFORMANCE METRICS
===================
Transcription Time: _____ s
Total E2E Time: _____ s
Concurrent Users Tested: _____
Memory Usage: _____ MB

BROWSER COMPATIBILITY
=====================
Chrome: [ ] Pass [ ] Fail
Firefox: [ ] Pass [ ] Fail
Safari: [ ] Pass [ ] Fail
Edge: [ ] Pass [ ] Fail

OVERALL ASSESSMENT
==================
[ ] READY FOR PRODUCTION
[ ] READY WITH KNOWN ISSUES
[ ] NEEDS MORE WORK

Notes:
______________________________________________________________________
```

---

## Next Steps (Phase 4)

- Deployment guide (Docker, cloud platforms)
- Performance optimization (caching, CDN)
- Advanced features (video library, student dashboard)
- Production monitoring and logging

---

## Testing Checklist Summary

- [ ] All four scenarios completed
- [ ] All performance metrics acceptable
- [ ] No critical errors encountered
- [ ] Automated tests passing
- [ ] Browsers tested: Chrome + Firefox minimum
- [ ] Concurrent user limit verified
- [ ] Error handling validated
- [ ] Results documented

**Phase 3 Complete When:** ✅ All checkboxes marked

---

**Status:** Ready for manual testing. Proceed with Scenario 1 testing when ready.
