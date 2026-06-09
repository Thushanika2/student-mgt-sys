from flask import jsonify, request
from app.models.student_model import Student
from app.models.course_model import Course
from app.extensions import db
from app.models.enrollment_model import Enrollment
from datetime import date


def _validate_enrollment_payload(data, enrollment_id=None):
    errors = []
    if not data:
        return ["Request body is required."]
    

    student_id = data.get("student_id")
    if not student_id:
        errors.append("Student is required.")

    else:
        student = Student.query.get(int(student_id))
        if not student:
            errors.append("Invalid student selected.")


    course_id = data.get("course_id")
    if not course_id:
        errors.append("Course is required.")

    else:
        course = Course.query.get(int(course_id))
        if not course:
            errors.append("Invalid course selected.")


    enrollment_date = data.get("enrollment_date")
    if not enrollment_date:
        errors.append("Enrollment date is required.")
    else:
        try:
            date.fromisoformat(str(enrollment_date))
        except ValueError:
            errors.append("Enrollment date must be a valid date (YYYY-MM-DD).")

    status = data.get("status")
    if not status or str(status).strip() == "":
        errors.append("Status is required.")

    return errors


def create_enrollment():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_enrollment_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        enrollment = Enrollment(
            student_id=int(data.get("student_id")),
            course_id=int(data.get("course_id")),
            enrollment_date=date.fromisoformat(str(data.get("enrollment_date"))),
            status=data.get("status").strip(),   
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({"message": "enrollment created successfully.", "enrollment": enrollment.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500


def get_enrollments():
    enrollments = Enrollment.query.all()
    return jsonify({"enrollments": [s.to_dict() for s in enrollments]}), 200


def get_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"error": "enrollment not found."}), 404
    return jsonify({"enrollment": enrollment.to_dict()}), 200


def update_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"error": "enrollment not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided to update."}), 400

    errors = _validate_enrollment_payload(data, enrollment_id=enrollment_id)
    if errors:
        return jsonify({"errors": errors}), 400


    try:
        enrollment.student_id = int(data.get("student_id"))
        enrollment.course_id = int(data.get("course_id"))
        enrollment.enrollment_date = date.fromisoformat(str(data.get("enrollment_date")))
        enrollment.status = data.get("status").strip()
        db.session.commit()
        return jsonify({"message": "enrollment updated successfully.", "enrollment": enrollment.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500


def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"error": "enrollment not found."}), 404
    try:
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({"message": "enrollment deleted successfully."}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500
