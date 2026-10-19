import streamlit as st
from supabase import create_client


@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def save_analysis(email, article, r, score, grade):
    """Returns (saved, error_message)."""
    try:
        get_client().table("analyses").insert({
            "user_email": email,
            "title": article.get("title"),
            "url": article.get("url"),
            "score": score,
            "grade": grade,
            "result": r,
        }).execute()
        return True, ""
    except Exception as e:
        return False, str(e)


def load_history(email, limit=20):
    try:
        resp = (
            get_client()
            .table("analyses")
            .select("*")
            .eq("user_email", email)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data, ""
    except Exception as e:
        return [], str(e)