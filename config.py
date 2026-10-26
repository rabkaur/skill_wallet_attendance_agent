"""Central settings. All processing is local/offline."""
SUSTAIN_SECONDS = 10      # presence needed before attendance is marked
MAX_MISSING = 5           # seconds a face may vanish before its track is dropped
INACTIVE_LIMIT = 60       # seconds without movement = fully inactive
MOVE_EPS = 0.02           # normalised movement below this counts as "still"
INTERVAL = 30             # seconds per engagement window
FPS = 5                   # processing rate
DB_PATH = "data/session.db"
W_ATTENTION, W_MOTION, W_ACTIVITY = 0.5, 0.2, 0.3   # per-student visual score
W_VISUAL, W_AUDIO = 0.8, 0.2                        # multimodal fusion
