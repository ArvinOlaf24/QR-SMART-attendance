from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.utils.distance import calculate_distance
from app.utils.supabase_client import get_supabase

attendance_bp = Blueprint("attendance", __name__)

MAX_DISTANCE_METERS = 20


@attendance_bp.route("/attendance", methods=["GET", "POST"])
def attendance():
    course_id = request.args.get("courseId") or request.form.get("course_id")
    course_code = request.args.get("courseCode") or request.form.get("course_code")
    lat = request.args.get("lat", type=float) or request.form.get("lat", type=float)
    lng = request.args.get("lng", type=float) or request.form.get("lng", type=float)

    if not course_id:
        flash("Invalid attendance link.", "error")
        return redirect(url_for("main.index"))

    supabase = get_supabase()
    class_result = (
        supabase.table("classes").select("*").eq("course_id", course_id).single().execute()
    )
    class_details = class_result.data

    if request.method == "GET":
        return render_template(
            "attendance.html",
            class_details=class_details,
            course_id=course_id,
            course_code=course_code,
            lat=lat,
            lng=lng,
        )

    matric_number = request.form.get("matric_number", "").strip().upper()
    name = request.form.get("name", "").strip().upper()
    user_lat = request.form.get("user_lat", type=float)
    user_lng = request.form.get("user_lng", type=float)

    if not matric_number:
        flash("Matriculation number is required.", "error")
        return _render_attendance_error(
            class_details, course_id, course_code, lat, lng
        )

    if user_lat is None or user_lng is None or lat is None or lng is None:
        flash("Location is required to mark attendance.", "error")
        return _render_attendance_error(
            class_details, course_id, course_code, lat, lng
        )

    distance = calculate_distance(user_lat, user_lng, lat, lng)
    if distance > MAX_DISTANCE_METERS:
        flash(
            f"You must be within {MAX_DISTANCE_METERS} meters of the lecture venue.",
            "error",
        )
        return render_template(
            "attendance.html",
            class_details=class_details,
            course_id=course_id,
            course_code=course_code,
            lat=lat,
            lng=lng,
            user_distance=distance,
            is_within_range=False,
        )

    fetch_result = (
        supabase.table("classes")
        .select("attendees")
        .eq("course_id", course_id)
        .single()
        .execute()
    )
    if fetch_result.data is None:
        flash("Class not found.", "error")
        return redirect(url_for("main.index"))

    attendees = fetch_result.data.get("attendees") or []
    if any(a.get("matric_no") == matric_number for a in attendees):
        flash("This matriculation number has already been registered.", "error")
        return _render_attendance_error(
            class_details, course_id, course_code, lat, lng, distance
        )

    new_attendee = {
        "matric_no": matric_number,
        "name": name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    updated_attendees = attendees + [new_attendee]

    update_result = (
        supabase.table("classes")
        .update({"attendees": updated_attendees})
        .eq("course_id", course_id)
        .execute()
    )

    if not update_result.data:
        flash("Error marking attendance. Please try again.", "error")
        return _render_attendance_error(
            class_details, course_id, course_code, lat, lng, distance
        )

    flash("Attendance marked successfully.", "success")
    return redirect(url_for("main.success"))


def _render_attendance_error(
    class_details, course_id, course_code, lat, lng, user_distance=None
):
    return render_template(
        "attendance.html",
        class_details=class_details,
        course_id=course_id,
        course_code=course_code,
        lat=lat,
        lng=lng,
        user_distance=user_distance,
        is_within_range=False,
    )
