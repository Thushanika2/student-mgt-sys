from datetime import date

from flask import jsonify, request

from app.extensions import db
from app.models.student_model import Student


def _validate_student_payload(data, student_id=None):
    errors = []
    if not data:
        return ["Request body is required."]
    

    first_name = data.get("first_name")
    if not first_name or str(first_name).strip() == "":
        errors.append("First name is required.")

    elif not str(first_name).strip().isalpha():
        errors.append("First name must contain only letters.")

    elif len(str(first_name).strip()) < 2 or len(str(first_name).strip()) > 50:
        errors.append("First name must be 2-50 characters.")


    last_name = data.get("last_name")
    if not last_name or str(last_name).strip() == "":
        errors.append("Last name is required.")

    elif not str(last_name).strip().isalpha():
        errors.append("Last name must contain only letters.")

    elif len(str(last_name).strip()) < 2 or len(str(last_name).strip()) > 50:
        errors.append("Last name must be 2-50 characters.")


    email = data.get("email")
    if not email or str(email).strip() == "":
        errors.append("Email is required.")

    else:
        em = str(email).strip()
        if "@" not in em or "." not in em.split("@")[-1]:
            errors.append("Please enter a valid email address.")

        else:
            q = Student.query.filter(Student.email == em)
            if student_id:
                q = q.filter(Student.student_id != student_id)

            if q.first():
                errors.append("Email already exists.")


    dob = data.get("date_of_birth")
    if not dob:
        errors.append("Date of birth is required.")

    else:
        try:
            dob_date = date.fromisoformat(str(dob))
            if dob_date >= date.today():
                errors.append("Date of birth can't be a future date.")

        except ValueError:
            errors.append("Date of birth must be a valid date (YYYY-MM-DD).")
                
    return errors


def create_student():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_student_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400


    try:
        student = Student(
            first_name=data.get("first_name").strip(),
            last_name=data.get("last_name").strip(),
            email=data.get("email").strip(),
            date_of_birth=date.fromisoformat(str(data.get("date_of_birth"))),
        )

        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Student created successfully.", "student": student.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500


def get_students():
    students = Student.query.all()
    return jsonify({"students": [s.to_dict() for s in students]}), 200


def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found."}), 404
    return jsonify({"student": student.to_dict()}), 200


def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided to update."}), 400

    errors = _validate_student_payload(data, student_id=student_id)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        student.first_name = data.get("first_name").strip()
        student.last_name = data.get("last_name").strip()
        student.email = data.get("email").strip()
        student.date_of_birth = date.fromisoformat(str(data.get("date_of_birth")))

        db.session.commit()
        return jsonify({"message": "Student updated successfully.", "student": student.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500


def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found."}), 404
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred.","details": str(e)}), 500
