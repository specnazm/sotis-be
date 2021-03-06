from flask import Blueprint, request, jsonify, Response
from testingapp import db
from testingapp.models.testmodels import Subject
from testingapp.models.usermodels import User
from flask_jwt_extended import jwt_required, get_jwt_identity

from testingapp.utils.authutils import get_user_if_logged_in
from testingapp.utils.roleconstants import TEACHER

subject_bp = Blueprint('subject', __name__)


@subject_bp.route('/subject', methods=['POST'])
def create_subject():
    try:
        user = get_user_if_logged_in()
        if not user:
            return Response(status=401)

        data = request.json
        name = data.get('name', 'NO NAME')
        description = data.get('description', '')
        points = data['points']
        teachers = data.get('teachers', [])
        students = data.get('students', [])

        new_subject = Subject(name=name, description=description, points=points)
        db.session.add(new_subject)
        db.session.commit()
        return jsonify(new_subject.to_dict())
    except Exception as error:
        print(error)
        return Response(status=400)

@subject_bp.route('/subject', methods=['GET'])
@jwt_required
def get_all():
    user = get_user_if_logged_in()
    if not user:
        return Response(status=401)

    return jsonify([sub.to_dict(rules = ('-tests', '-students', 'teachers.id')) for sub in user.subjects])
