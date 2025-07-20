from flask import Blueprint, request, jsonify
from models import User
from utils.auth import check_password
from flask_jwt_extended import create_access_token


auth_api = Blueprint('auth_api', __name__)

# Login de l'utilisateur
@auth_api.route('/users', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'msg': 'Email and password are required'}), 400
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user and check_password(data['password'], user.password):
            token = create_access_token(
                identity=user.id,
                additional_claims={
                    "roles": user.roles  # Assure-toi que user.role vaut 'admin' ou 'client'
                }
               
                 )
            return jsonify({'access_token': token}), 200
        return jsonify({'message': "L'email ou le mot de passe n'existe pas"}), 401
    except Exception as e:
        return jsonify({'message': "Erreur lors de la connexion"}), 500