from flask import current_app, session
from supabase import Client, create_client


def get_supabase() -> Client:
    return create_client(
        current_app.config["SUPABASE_URL"],
        current_app.config["SUPABASE_ANON_KEY"],
    )


def get_authenticated_supabase() -> Client:
    client = get_supabase()
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    if access_token and refresh_token:
        client.auth.set_session(access_token, refresh_token)
    return client
