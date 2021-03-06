from datetime import datetime, timezone
from testingapp import db, app, flask_bcrypt
from testingapp import db, app
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, \
    fresh_jwt_required, get_jti, get_raw_jwt

from testingapp.models.tokenblockmodel import TokenBlocklist
from testingapp.models.usermodels import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def signup():
    data = request.get_json()
    new_user = User(first_name=data['first_name'], last_name=data['last_name'], email=data['email'],
                    password=data["password"], role="teacher")
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as error:
        return jsonify({"msg": str(error.orig)}), 400

    return jsonify(new_user.to_dict())


@auth_bp.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    user = User.query.filter_by(email=auth["email"]).first()
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    if user.check_password(auth["password"]):
        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token)
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@auth_bp.route('/logout', methods=['DELETE'])
def logout():
    jti =  get_raw_jwt().get('jti', 'none') # outdated dokumentacija, nema vise get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    #db.session.add(TokenBlocklist(jti=jwt, created_at=now))
    #db.session.commit()
    return jsonify({"msg":"JWT revoked"})

# @app.route("/refresh", methods=["POST"])
# @jwt_required(fresh_jwt_required)
# def refresh():
#     identity = get_jwt_identity()
#     access_token = create_access_token(identity=identity, fresh=False)
#     return jsonify(access_token=access_token)
