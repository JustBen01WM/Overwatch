import time
import streamlit as st

PER_VISITOR_LIMIT = 5
COOLDOWN_SECONDS = 30
DAILY_LIMIT = 100


@st.cache_resource
def _daily_counter():
    return {"day": time.strftime("%Y-%m-%d"), "count": 0}


def check_and_record():
    """Returns (allowed, message). Call it once before each analysis."""
    daily = _daily_counter()
    today = time.strftime("%Y-%m-%d")
    if daily["day"] != today:
        daily["day"] = today
        daily["count"] = 0

    if daily["count"] >= DAILY_LIMIT:
        return False, "Overwatch has reached its daily limit. Please try again tomorrow."

    used = st.session_state.get("used", 0)
    if used >= PER_VISITOR_LIMIT:
        return False, f"You've used your {PER_VISITOR_LIMIT} analyses for this visit."

    wait = COOLDOWN_SECONDS - (time.time() - st.session_state.get("last_time", 0))
    if wait > 0:
        return False, f"Please wait {int(wait) + 1} more seconds before the next analysis."

    st.session_state["used"] = used + 1
    st.session_state["last_time"] = time.time()
    daily["count"] += 1
    return True, ""