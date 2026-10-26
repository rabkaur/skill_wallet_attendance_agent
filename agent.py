"""Assistive teaching agent: transparent rules over engagement windows. Suggests, never enforces."""
def suggest(w):
    if not w: return []
    cur, tips = w[-1], []
    if len(w) >= 2 and w[-2]["score"] - cur["score"] >= 15:
        tips.append("Engagement dropped sharply. Try a quick poll, a question to the class or a short activity.")
    if cur["attention"] < 50:
        tips.append("Many learners are looking away. Change the delivery mode, e.g. a demo, visual or movement break.")
    if cur["inactivity"] > 40:
        tips.append("A large share of the class has been still for a long time. Consider a 2-minute stretch break.")
    if cur["audio"] < 0.05 and len(w) >= 2 and w[-2]["audio"] < 0.05:
        tips.append("Little interaction for two windows. Invite discussion or pair-share to encourage participation.")
    if cur["audio"] > 0.7 and cur["attention"] < 60:
        tips.append("High noise with low attention. A short reset or clear instructions may help classroom management.")
    if len(w) >= 3 and all(x["score"] >= 70 for x in w[-3:]):
        tips.append("Engagement has been strong for a while. Keep the current pacing.")
    return tips or ["No concerns detected. Engagement is within a normal range."]
