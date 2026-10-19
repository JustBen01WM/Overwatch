import time
from datetime import datetime, timezone

import streamlit as st
from db import count_since

PER_USER_DAILY = 10
GLOBAL_DAILY = 100
COOLDOWN_SECONDS = 30


def check_limits(email):
    """Returns (allowed, message). Call once before each analysis."""
    wait = COOLDOWN_SECONDS - (time.time() - st.session_state.get("last_time", 0))
    if wait > 0:
        return False, f"Please wait {int(wait) + 1} more seconds before the next analysis."

    start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()

    mine, err1 = count_since(start, email)
    total, err2 = count_since(start)
    if err1 or err2:
        return False, "Couldn't check your usage right now. Please try again in a moment."

    if mine >= PER_USER_DAILY:
        return False, f"You've used your {PER_USER_DAILY} analyses for today. Come back tomorrow."
    if total >= GLOBAL_DAILY:
        return False, "Overwatch has reached its daily limit. Please try again tomorrow."

    st.session_state["last_time"] = time.time()
    return True, ""