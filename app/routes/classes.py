import csv
import io
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from openpyxl import Workbook

from app.utils.auth_helpers import get_current_lecturer, login_required
from app.utils.qr_code import generate_qr_data_url
from app.utils.supabase_client import get_authenticated_supabase

classes_bp = Blueprint("classes", __name__)


@classes_bp.route("/class-details")
@login_required
def class_details():
    lecturer = get_current_lecturer()
    return render_template("class_details.html", lecturer=lecturer)


@classes_bp.route("/class-schedule", methods=["GET", "POST"])
@login_required
def class_schedule():
    lecturer = get_current_lecturer()
    if not lecturer:
        flash("Lecturer profile not found.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("class_schedule.html")

    course_title = request.form.get("course_title", "").strip()
    course_code = request.form.get("course_code", "").strip()
    lecture_venue = request.form.get("lecture_venue", "").strip()
    time_value = request.form.get("time", "").strip()
    date_value = request.form.get("date", "").strip()
    note = request.form.get("note", "").strip()
    lat = request.form.get("lat", type=float)
    lng = request.form.get("lng", type=float)

    if not all([course_title, course_code, lecture_venue, time_value, date_value, lat, lng]):
        flash("Please complete all required fields and select a location.", "error")
        return render_template("class_schedule.html"), 400

    location_geography = f"SRID=4326;POINT({lng} {lat})"
    combined_dt = datetime.strptime(f"{date_value} {time_value}", "%Y-%m-%d %H:%M")

    supabase = get_authenticated_supabase()
    app_url = current_app.config["APP_URL"].rstrip("/")

    try:
        placeholder_link = (
            f"{app_url}/attendance?courseCode={course_code}&time={time_value}"
            f"&lectureVenue={lecture_venue}&lat={lat}&lng={lng}"
        )
        qr_data_url = generate_qr_data_url(placeholder_link)

        insert_result = (
            supabase.table("classes")
            .insert(
                {
                    "course_title": course_title,
                    "course_code": course_code,
                    "time": combined_dt.isoformat(),
                    "date": datetime.strptime(date_value, "%Y-%m-%d").isoformat(),
                    "location": location_geography,
                    "note": note,
                    "qr_code": qr_data_url,
                    "lecturer_id": lecturer.get("lecturer_id"),
                    "location_name": lecture_venue,
                }
            )
            .execute()
        )

        if not insert_result.data:
            raise ValueError("Failed to create class schedule.")

        course_id = insert_result.data[0]["course_id"]
        registration_link = (
            f"{app_url}/attendance?courseId={course_id}&time={time_value}"
            f"&courseCode={course_code}&lat={lat}&lng={lng}"
        )

        flash("Class schedule created successfully.", "success")
        return render_template(
            "class_schedule.html",
            show_qr=True,
            qr_link=registration_link,
        )
    except Exception as exc:
        flash(f"Error creating class schedule: {exc}", "error")
        return render_template("class_schedule.html"), 400


@classes_bp.route("/previous-class")
@login_required
def previous_class():
    lecturer = get_current_lecturer()
    if not lecturer:
        flash("Lecturer profile not found.", "error")
        return redirect(url_for("auth.login"))

    supabase = get_authenticated_supabase()
    result = (
        supabase.table("classes")
        .select("*")
        .eq("lecturer_id", lecturer.get("lecturer_id"))
        .execute()
    )
    classes = result.data or []
    return render_template("previous_class.html", classes=classes)


@classes_bp.route("/previous-class/<course_id>/attendees")
@login_required
def view_attendees(course_id):
    supabase = get_authenticated_supabase()
    result = (
        supabase.table("classes").select("*").eq("course_id", course_id).single().execute()
    )
    class_item = result.data
    if not class_item:
        flash("Class not found.", "error")
        return redirect(url_for("classes.previous_class"))

    return render_template("attendance_list.html", class_item=class_item)


@classes_bp.route("/export/csv/<course_id>")
@login_required
def export_csv(course_id):
    try:
        class_item = _get_class_or_404(course_id)
    except ValueError:
        flash("Class not found.", "error")
        return redirect(url_for("classes.previous_class"))
    attendees = class_item.get("attendees") or []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Matric No", "Attended At"])
    for attendee in attendees:
        writer.writerow(
            [
                attendee.get("name", ""),
                attendee.get("matric_no", ""),
                attendee.get("timestamp", ""),
            ]
        )

    buffer = io.BytesIO(output.getvalue().encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"attendance_list_{course_id}.csv",
    )


@classes_bp.route("/export/excel/<course_id>")
@login_required
def export_excel(course_id):
    try:
        class_item = _get_class_or_404(course_id)
    except ValueError:
        flash("Class not found.", "error")
        return redirect(url_for("classes.previous_class"))
    attendees = class_item.get("attendees") or []

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    sheet.append(["Name", "Matric No", "Attended At"])
    for attendee in attendees:
        sheet.append(
            [
                attendee.get("name", ""),
                attendee.get("matric_no", ""),
                attendee.get("timestamp", ""),
            ]
        )

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"attendance_list_{course_id}.xlsx",
    )


def _get_class_or_404(course_id):
    supabase = get_authenticated_supabase()
    result = (
        supabase.table("classes").select("*").eq("course_id", course_id).single().execute()
    )
    if not result.data:
        raise ValueError("Class not found")
    return result.data
