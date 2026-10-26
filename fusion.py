"""Multimodal fusion: head pose + movement + inactivity (visual) combined with audio activity."""
import config

def student_score(s):
    attention = 1.0 if s["facing"] else 0.3
    motion = 0.6 if s["move"] < config.MOVE_EPS else 1.0
    activity = max(0.0, 1 - s["inactive"] / config.INACTIVE_LIMIT)
    return 100 * (config.W_ATTENTION * attention + config.W_MOTION * motion + config.W_ACTIVITY * activity)

def fuse(samples, audio):
    """samples: list of per-frame student lists collected during one window."""
    flat = [s for frame in samples for s in frame]
    if not flat:
        return {"score": 0, "attention": 0, "inactivity": 0, "audio": round(audio, 2), "students": 0}
    visual = sum(student_score(s) for s in flat) / len(flat)
    return {"score": round(config.W_VISUAL * visual + config.W_AUDIO * 100 * audio, 1),
            "attention": round(100 * sum(s["facing"] for s in flat) / len(flat), 1),
            "inactivity": round(100 * sum(s["inactive"] > 20 for s in flat) / len(flat), 1),
            "audio": round(audio, 2), "students": len(samples[-1])}
