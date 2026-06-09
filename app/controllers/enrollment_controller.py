from flask import jsonify, request

from app.extensions import db
from app.models.enrollment_model import Enrollment


def _validate_enrollment_payload(data, enrollment_id=None):
    errors = []
    if not data:
        return ["Request body is required."]
    
    existing_enrollment_id = Enrollment.query.filter_by(enrollment_id=data["enrollment_id"]).first()
    if existing_enrollment_id:
        return jsonify({"ERROR": "enrollment_id already exists"}), 400
    
    student = data.get("student_id")
    if student is None or str(student).strip() == "":
        errors.append("Invalid student selected")

    course = data.get("course_id")
    if course is None or str(course).strip() == "":
        errors.append("Invalid course selected")

    enrollment_date = data.get("enrollment_date")
    if enrollment_date is None or str(enrollment_date).strip() == "":
        errors.append("enrollment_date is required.")

    status = data.get("status")
    if status is None or str(status).strip() == "":
        errors.append("status is required.")

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
            enrollment_id=data.get("enrollment_id").strip(),
            student_id=data.get("student_id").strip(),
            course_id=data.get("course_id").strip(),
            enrollment_date=data.get("enrollment_date").strip(),
            status=data.get("status").strip(),   
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({"message": "enrollment created successfully.", "enrollment": enrollment.to_dict()}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


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
        enrollment.enrollment_id = data.get("enrollment_id").strip()
        enrollment.student_id = data.get("student_id").strip()
        enrollment.course_id = data.get("course_id").strip()
        enrollment.enrollment_date = data.get("enrollment_date").strip()
        enrollment.status = data.get("status").strip()
        db.session.commit()
        return jsonify({"message": "enrollment updated successfully.", "enrollment": enrollment.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"error": "enrollment not found."}), 404
    try:
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({"message": "enrollment deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500
