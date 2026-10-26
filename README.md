# Multimodal Attendance & Engagement Agent (Skill Wallet)

Privacy-preserving, fully offline classroom intelligence: automatic attendance, engagement analytics and AI teaching suggestions.

## Pre-requisites
Python 3.8+, VS Code, Git, Chrome/Firefox/Edge. Hardware: i5 8th gen / Ryzen 5, 8 GB RAM (16 GB recommended), 256 GB SSD, webcam + microphone.
Install: `pip install -r requirements.txt`

## Project Workflow
Video / Audio input -> Vision module (faces, tracking, head pose, movement, inactivity) + Audio module (speech activity)
-> Sustained-presence attendance + Multimodal fusion -> Engagement score per window -> Agent (suggestions) -> SQLite -> Flask dashboard.

```
Dashboard (HTML/CSS/JS)  <->  Flask API (app.py)
        Session loop: vision.py + audio.py -> fusion.py -> agent.py
        Local storage: SQLite (data/session.db) + CSV export    [no cloud calls]
```

## EPIC 1: Requirements Specification and Environment Setup
- Objectives: automated attendance, engagement analysis, AI suggestions, privacy by design.
- Architecture & workflow above; `config.py` holds all tunables.
- Setup: create venv, `pip install -r requirements.txt`, test camera index 0 and microphone.

## EPIC 2: Vision Module Development (`vision.py`)
- Video input: live camera index, or recorded video file (`--source`).
- Face detection (OpenCV Haar frontal + profile) and anonymous centroid tracking (Student-N, no biometrics stored).
- Sustained presence: attendance only after `SUSTAIN_SECONDS` of accumulated presence; tracks survive short dropouts.
- Behaviour features: head pose proxy (frontal vs profile = facing/away), normalised movement, inactivity duration.

## EPIC 3: Audio Module Development (`audio.py`)
- Audio input: microphone (sounddevice) or WAV file (`--wav`).
- Energy-based speech detection with adaptive noise floor; reports interaction ratio over a time window.

## EPIC 4: AI Implementation (`fusion.py`)
- Per-student visual score = 0.5 attention + 0.2 motion + 0.3 activity.
- Multimodal fusion: class score = 0.8 visual + 0.2 audio. Weights in `config.py`.

## EPIC 5: Analytics and Recommendation Engine (`agent.py`, `storage.py`)
- Engagement windows (default 30 s) give session trends: drops, peaks, pacing.
- Rule-based agent produces explainable teaching suggestions (polls, breaks, discussion, classroom management). Decision support only.
- Timestamped attendance logs and engagement history in local SQLite; CSV export.

## EPIC 6: Interface, Testing, and Deployment (`app.py`, `templates/`)
- Run: `python app.py --demo` (synthetic classroom, no hardware) or `python app.py --source 0`, then open http://127.0.0.1:5000 and press Start.
- Test: demo mode for pipeline checks; recorded classroom videos for accuracy (compare marked vs. true attendance); watch FPS on target hardware.
- Deployment: local machine, no internet needed; data never leaves the device.

## Conclusion
The system replaces manual roll calls with sustained-presence attendance and turns multimodal signals into actionable engagement insight, while staying offline and anonymous.
Limitations: Haar-based pose is coarse; upgrade path = MediaPipe/Dlib landmarks for true head pose, and VAD (e.g. WebRTC VAD) for audio.
