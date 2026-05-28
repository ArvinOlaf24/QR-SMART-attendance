from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.utils.auth_helpers import clear_auth_session, store_auth_session
from app.utils.supabase_client import get_authenticated_supabase, get_supabase

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    phone_number = request.form.get("phone_number", "").strip()

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("register.html"), 400

    if not all([full_name, email, phone_number, password]):
        flash("Please fill in all fields.", "error")
        return render_template("register.html"), 400

    supabase = get_supabase()
    try:
        auth_response = supabase.auth.sign_up({"email": email, "password": password})
        if auth_response.user is None:
            raise ValueError("Registration failed. Please try again.")

        supabase.table("lecturers").insert(
            {
                "fullName": full_name,
                "email": email,
                "phone_number": phone_number,
            }
        ).execute()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))
    except Exception as exc:
        flash(str(exc), "error")
        return render_template("register.html"), 400


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    supabase = get_supabase()
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        store_auth_session(auth_response)
        flash("Login successful.", "success")
        return redirect(url_for("classes.class_details"))
    except Exception as exc:
        flash(str(exc), "error")
        return render_template("login.html"), 400


@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        get_authenticated_supabase().auth.sign_out()
    except Exception:
        pass
    clear_auth_session()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.index"))
