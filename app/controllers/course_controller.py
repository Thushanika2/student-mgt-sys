from flask import jsonify, request
from app.models.lecturer_model import Lecturer
from app.extensions import db
from app.models.course_model import Course


def _validate_course_payload(data, course_id=None):
    errors = []
    if not data:
        return ["Request body is required."]
    
    course_code = data.get("course_code")
    if not course_code or str(course_code).strip() == "":
        errors.append("Course code is required.")

    else:
        q = Course.query.filter(Course.course_code == str(course_code).strip())
        if course_id:
            q = q.filter(Course.course_id != course_id)

        if q.first():
            errors.append("Course code already exists.")
    

    course_name = data.get("course_name")
    if not course_name or str(course_name).strip() == "":
        errors.append("Course name is required.")

    elif len(str(course_name).strip()) < 3:
        errors.append("Course name must be at least 3 characters.")


    credits = data.get("credits")
    if credits is None:
        errors.append("Credits is required.")

    else:
        try:
            credits_val = int(credits)
            if credits_val < 1 or credits_val > 6:
                errors.append("Credits must be between 1 and 6.")
        except (TypeError, ValueError):
            errors.append("Credits must be a valid number.")


    lecturer_id = data.get("lecturer_id")
    if not lecturer_id:
        errors.append("Lecturer is required.")

    else:
        lecturer = Lecturer.query.get(int(lecturer_id))
        if not lecturer:
            errors.append("Invalid lecturer selected.")

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
            credits=int(data.get("credits")),
            lecturer_id=int(data.get("lecturer_id")),
        )
        db.session.add(course)
        db.session.commit()
        return jsonify({"message": "course created successfully.", "course": course.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500


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
        course.credits = int(data.get("credits"))
        course.lecturer_id = int(data.get("lecturer_id"))
        db.session.commit()
        return jsonify({"message": "course updated successfully.", "course": course.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500


def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "course not found."}), 404
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "course deleted successfully."}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500
