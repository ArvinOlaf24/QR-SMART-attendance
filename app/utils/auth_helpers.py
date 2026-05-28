from functools import wraps

from flask import flash, redirect, session, url_for

from app.utils.supabase_client import get_authenticated_supabase


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("access_token"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def get_current_lecturer():
    email = session.get("user_email")
    if not email:
        return None

    supabase = get_authenticated_supabase()
    result = (
        supabase.table("lecturers").select("*").eq("email", email).single().execute()
    )
    return result.data


def store_auth_session(auth_response):
    session["access_token"] = auth_response.session.access_token
    session["refresh_token"] = auth_response.session.refresh_token
    session["user_email"] = auth_response.user.email


def clear_auth_session():
    session.pop("access_token", None)
    session.pop("refresh_token", None)
    session.pop("user_email", None)
