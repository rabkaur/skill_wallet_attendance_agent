"""Multimodal Attendance & Engagement Agent. Run: python app.py [--demo | --source 0|video.mp4] [--wav file.wav]"""
import argparse, threading, time
from datetime import datetime
from flask import Flask, jsonify, render_template, Response
import config, storage, fusion, agent
from audio import AudioProcessor

app = Flask(__name__)
S = {"running": False, "students": [], "attendance": {}, "windows": [], "suggestions": [], "audio": 0.0}
ARGS = None

def now_s(): return datetime.now().strftime("%H:%M:%S")

def run_session():
    import cv2
    from vision import VisionProcessor, DemoVision
    storage.reset()
    S.update(students=[], attendance={}, windows=[], suggestions=[], running=True)
    vis = DemoVision() if ARGS.demo else VisionProcessor()
    cap = None if ARGS.demo else cv2.VideoCapture(int(ARGS.source) if ARGS.source.isdigit() else ARGS.source)
    aud = AudioProcessor(wav=ARGS.wav, demo=ARGS.demo, use_mic=not ARGS.no_mic); aud.start()
    samples, win_start = [], time.time()
    while S["running"]:
        t = time.time()
        frame = None
        if cap:
            ok, frame = cap.read()
            if not ok: break
        studs = vis.process(frame, t)
        S["students"], samples = studs, samples + [studs]
        for s in studs:                                     # sustained-presence attendance
            a = S["attendance"].get(s["id"])
            if a: a["last_seen"], a["present_seconds"] = now_s(), s["present"]
            elif s["present"] >= config.SUSTAIN_SECONDS:
                S["attendance"][s["id"]] = {"marked_at": now_s(), "last_seen": now_s(), "present_seconds": s["present"]}
            if s["id"] in S["attendance"]:
                a = S["attendance"][s["id"]]
                storage.upsert_attendance(s["id"], a["marked_at"], a["last_seen"], a["present_seconds"])
        S["audio"] = round(aud.interaction(10), 2)
        if t - win_start >= config.INTERVAL:                 # close engagement window
            w = fusion.fuse(samples, aud.interaction(config.INTERVAL)); w["ts"] = now_s()
            S["windows"].append(w); storage.add_window(w["ts"], w)
            S["suggestions"] = agent.suggest(S["windows"]); storage.add_suggestions(w["ts"], S["suggestions"])
            samples, win_start = [], t
        time.sleep(max(0, 1 / config.FPS - (time.time() - t)))
    S["running"] = False; aud.stop = True
    if cap: cap.release()

@app.route("/")
def index(): return render_template("dashboard.html")
@app.route("/api/state")
def state(): return jsonify(S)
@app.route("/api/start", methods=["POST"])
def start():
    if not S["running"]: threading.Thread(target=run_session, daemon=True).start()
    return jsonify(ok=True)
@app.route("/api/stop", methods=["POST"])
def stop(): S["running"] = False; return jsonify(ok=True)
@app.route("/api/attendance.csv")
def csv_export():
    return Response(storage.attendance_csv(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=attendance.csv"})

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true"); p.add_argument("--source", default="0")
    p.add_argument("--wav"); p.add_argument("--no-mic", action="store_true")
    ARGS = p.parse_args()
    if ARGS.demo: config.SUSTAIN_SECONDS, config.INTERVAL = 5, 10
    app.run(host="127.0.0.1", port=5000, debug=False)
