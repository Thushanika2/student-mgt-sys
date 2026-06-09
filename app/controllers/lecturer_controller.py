from flask import jsonify, request

from app.extensions import db
from app.models.lecturer_model import Lecturer


def _validate_lecturer_payload(data, lecturer_id=None):
    errors = []
    if not data:
        return ["Request body is required."]
    
    existing_lecturer_id = Lecturer.query.filter_by(lecturer_id=data["lecturer_id"]).first()
    if existing_lecturer_id:
        return jsonify({"ERROR": "lecturer_id already exists"}), 400

    first_name = data.get("first_name")
    if first_name is None or str(first_name).strip() == "":
        errors.append("first_name is required.")

    last_name = data.get("last_name")
    if last_name is None or str(last_name).strip() == "":
        errors.append("last_name is required.")

    email = data.get("email")
    if email is None or str(email).strip() == "":
        errors.append("email is required.")
    elif str(email).strip():
        q = Lecturer.query.filter(Lecturer.email == str(email).strip())

    department = data.get("department")
    if department is None or str(department).strip() == "":
        errors.append("department is required.")

    return errors


def create_lecturer():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_lecturer_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        lecturer = Lecturer(
            first_name=data.get("first_name").strip(),
            last_name=data.get("last_name").strip(),
            email=data.get("email").strip(),
            department=data.get("department").strip(),
        )
        db.session.add(lecturer)
        db.session.commit()
        return jsonify({"message": "lecturer created successfully.", "lecturer": lecturer.to_dict()}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def get_lecturers():
    lecturers = Lecturer.query.all()
    return jsonify({"lecturers": [s.to_dict() for s in lecturers]}), 200


def get_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    if not lecturer:
        return jsonify({"error": "lecturer not found."}), 404
    return jsonify({"lecturer": lecturer.to_dict()}), 200


def update_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    if not lecturer:
        return jsonify({"error": "lecturer not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided to update."}), 400

    errors = _validate_lecturer_payload(data, lecturer_id=lecturer_id)
    if errors:
        return jsonify({"errors": errors}), 400


    try:
        lecturer.first_name = data.get("first_name").strip()
        lecturer.last_name = data.get("last_name").strip()
        lecturer.email = data.get("email").strip()
        lecturer.department = data.get("department").strip()
        db.session.commit()
        return jsonify({"message": "lecturer updated successfully.", "lecturer": lecturer.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def delete_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    if not lecturer:
        return jsonify({"error": "lecturer not found."}), 404
    try:
        db.session.delete(lecturer)
        db.session.commit()
        return jsonify({"message": "lecturer deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500
