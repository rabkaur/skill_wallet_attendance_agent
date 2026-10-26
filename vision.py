"""Face detection + anonymous centroid tracking + behaviour features. No identities stored."""
import math, random
import cv2
import config

class Track:
    def __init__(s, tid, c, now):
        s.id, s.c, s.last, s.present = f"Student-{tid}", c, now, 0.0
        s.facing, s.move, s.last_move = True, 0.0, now

    def d(s, now):
        return {"id": s.id, "facing": s.facing, "move": round(s.move, 3),
                "inactive": round(now - s.last_move, 1), "present": round(s.present, 1)}

class VisionProcessor:
    def __init__(s):
        base = cv2.data.haarcascades
        s.front = cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml")
        s.side = cv2.CascadeClassifier(base + "haarcascade_profileface.xml")
        s.tracks, s.nid, s.prev_t = {}, 1, None

    def detect(s, frame):
        g = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        dets = [(x + w / 2, y + h / 2, w, True) for x, y, w, h in s.front.detectMultiScale(g, 1.2, 5, minSize=(40, 40))]
        for x, y, w, h in s.side.detectMultiScale(g, 1.2, 5, minSize=(40, 40)):  # profile face ~ head turned away
            c = (x + w / 2, y + h / 2)
            if all(math.dist(c, d[:2]) > w * 0.6 for d in dets):
                dets.append((c[0], c[1], w, False))
        return dets

    def process(s, frame, now):
        dt = 0 if s.prev_t is None else now - s.prev_t
        s.prev_t = now
        free = dict(s.tracks)
        for cx, cy, w, facing in s.detect(frame):
            best = min(free.values(), key=lambda t: math.dist(t.c, (cx, cy)), default=None)
            if best and math.dist(best.c, (cx, cy)) < max(w * 1.5, 60):
                free.pop(best.id)
                best.move = math.dist(best.c, (cx, cy)) / w
                if best.move > config.MOVE_EPS: best.last_move = now
                best.c, best.last, best.facing = (cx, cy), now, facing
                best.present += dt
            else:
                t = Track(s.nid, (cx, cy), now); s.nid += 1; s.tracks[t.id] = t
        for tid in [k for k, t in s.tracks.items() if now - t.last > config.MAX_MISSING]:
            del s.tracks[tid]
        return [t.d(now) for t in s.tracks.values() if t.last == now]

class DemoVision:
    """Synthetic classroom so the whole pipeline can be tested without a camera."""
    def __init__(s, n=8):
        s.n, s.t0, s.prev, s.state = n, None, None, {}
    def process(s, frame, now):
        s.t0 = s.t0 or now
        dt = 0 if s.prev is None else now - s.prev; s.prev = now
        att = 0.85 if ((now - s.t0) // 40) % 2 == 0 else 0.35   # alternating engaged / distracted phases
        out = []
        for i in range(1, s.n + 1):
            st = s.state.setdefault(i, {"present": 0.0, "inactive": 0.0})
            st["present"] += dt
            moved = random.random() < att
            st["inactive"] = 0 if moved else st["inactive"] + dt
            out.append({"id": f"Student-{i}", "facing": random.random() < att,
                        "move": round(random.uniform(0.03, 0.2) if moved else 0.0, 3),
                        "inactive": round(st["inactive"], 1), "present": round(st["present"], 1)})
        return out
