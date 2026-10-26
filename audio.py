"""Speech/interaction detection from energy with an adaptive noise floor."""
import threading, time, wave, collections
import numpy as np

class AudioProcessor:
    def __init__(s, wav=None, demo=False, use_mic=True):
        s.wav, s.demo, s.use_mic = wav, demo, use_mic
        s.buf, s.floor, s.available, s.stop = collections.deque(maxlen=6000), 0.005, False, False

    def _push(s, rms):
        s.floor = 0.98 * s.floor + 0.02 * rms if rms < s.floor * 1.5 else s.floor
        s.buf.append((time.time(), rms > max(s.floor * 2.5, 0.01)))

    def start(s):
        target = s._demo if s.demo else s._wav if s.wav else s._mic if s.use_mic else None
        if target: threading.Thread(target=target, daemon=True).start()

    def _mic(s):
        try:
            import sounddevice as sd
            with sd.InputStream(channels=1, samplerate=16000, blocksize=1600,
                                callback=lambda d, *_: s._push(float(np.sqrt(np.mean(d ** 2))))):
                s.available = True
                while not s.stop: time.sleep(0.2)
        except Exception as e:
            print("[audio] microphone unavailable:", e)

    def _wav(s):
        with wave.open(s.wav) as w:
            s.available, n = True, int(w.getframerate() * 0.1)
            while not s.stop:
                raw = w.readframes(n)
                if not raw: break
                x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
                s._push(float(np.sqrt(np.mean(x ** 2)))); time.sleep(0.1)

    def _demo(s):
        s.available = True
        while not s.stop:
            talk = (time.time() // 25) % 3 != 0
            s.floor = 0.005; s._push(0.05 if talk and np.random.rand() < 0.6 else 0.002); time.sleep(0.1)

    def interaction(s, seconds=30):
        cut = time.time() - seconds
        v = [f for t, f in s.buf if t >= cut]
        return sum(v) / len(v) if v else 0.0
