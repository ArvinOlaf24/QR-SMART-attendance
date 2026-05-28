from flask import Flask

from app.config import Config
from app.routes.api import api_bp
from app.routes.attendance import attendance_bp
from app.routes.auth import auth_bp
from app.routes.classes import classes_bp
from app.routes.main import main_bp


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config.from_object(config_class)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(api_bp)

    # Legacy React Router paths
    @app.route("/registerLecturer")
    def legacy_register():
        from flask import redirect, url_for

        return redirect(url_for("auth.register"))

    @app.route("/loginLecturer")
    def legacy_login():
        from flask import redirect, url_for

        return redirect(url_for("auth.login"))

    @app.route("/classDetails")
    def legacy_class_details():
        from flask import redirect, url_for

        return redirect(url_for("classes.class_details"))

    @app.route("/classSchedule")
    def legacy_class_schedule():
        from flask import redirect, url_for

        return redirect(url_for("classes.class_schedule"))

    @app.route("/previousClass")
    def legacy_previous_class():
        from flask import redirect, url_for

        return redirect(url_for("classes.previous_class"))

    return app
