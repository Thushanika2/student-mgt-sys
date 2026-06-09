from app.routes.student_routes import student_bp
from app.routes.course_routes import course_bp
from app.routes.lecturer_routes import lecturer_bp
from app.routes.enrollment_routes import enrollment_bp


def  register_blueprint(app):
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(lecturer_bp)
    app.register_blueprint(enrollment_bp)