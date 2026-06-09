from flask import jsonify, request

from app.extensions import db
from app.models.course_model import Course


def _validate_course_payload(data, course_id=None):
    errors = []
    if not data:
        return ["Request body is required."]
    
    existing_course_id = Course.query.filter_by(course_id=data["course_id"]).first()
    if existing_course_id:
        return jsonify({"ERROR": "course_id already exists"}), 400
    
    existing_course_code = Course.query.filter_by(course_code=data["course_code"]).first()
    if existing_course_code:
        return jsonify({"ERROR": "course_code already exists"}), 400

    course_name = data.get("course_name")
    if course_name is None or str(course_name).strip() == "":
        errors.append("course_name is required.")

    if not (1 <= ["credits"] <= 6):
        errors.append("Credits must be between 1 and 6")

    lecturer = data.get("lecturer_id")
    if lecturer is None or str(lecturer).strip() == "":
        errors.append("Invalid lecturer selected")

    return errors


def create_course():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_course_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        course = Course(
            course_code=data.get("course_code").strip(),
            course_name=data.get("course_name").strip(),
            credits=data.get("credits").strip(),
            lecturer_id=data.get("lecturer_id").strip(),
        )
        db.session.add(course)
        db.session.commit()
        return jsonify({"message": "course created successfully.", "course": course.to_dict()}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def get_courses():
    courses = Course.query.all()
    return jsonify({"courses": [s.to_dict() for s in courses]}), 200


def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "course not found."}), 404
    return jsonify({"course": course.to_dict()}), 200


def update_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "course not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided to update."}), 400

    errors = _validate_course_payload(data, course_id=course_id)
    if errors:
        return jsonify({"errors": errors}), 400


    try:
        course.course_code = data.get("course_code").strip()
        course.course_name = data.get("course_name").strip()
        course.credits = data.get("credits").strip()
        course.lecturer_id = data.get("lecturer_id").strip()
        db.session.commit()
        return jsonify({"message": "course updated successfully.", "course": course.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "course not found."}), 404
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "course deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500
