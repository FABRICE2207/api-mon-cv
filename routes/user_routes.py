# Configuration pour le téléchargement de photos
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# UPLOAD_FOLDER = 'static/uploads'


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
from flask import Blueprint, request, jsonify
from models import User
from db import db
from utils.auth import hash_password, check_password
from flask_jwt_extended import create_access_token

api = Blueprint('user_api', __name__)

# =====================
# 🔐 Enregistrement utilisateur
# =====================
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'msg': "Tous les champs sont obligatoires"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'msg': "L'email est déjà utilisé"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': "Le nom d'utilisateur est déjà utilisé"}), 400

    user = User(username=username, email=email, password=hash_password(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': "Utilisateur inscrit avec succès"}), 201

# =====================
# 🔐 Connexion utilisateur
# =====================
@api.route('/update', methods=['POST'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_confir = data.get('passwordConfir')

    if username:
        user.username = username
    if email:
        user.email = email
    if password or password_confir:
        if password != password_confir:
            return jsonify({'message': 'Les mots de passe ne correspondent pas'}), 400
        user.password = hash_password(password)

    db.session.commit()

    return jsonify({'message': 'Utilisateur mis à jour avec succès'}), 200


# @api.route('/uploads/<filename>', methods=['GET'])
# def uploaded_file(filename):
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Liste tous les utilisateurs
@api.route('/liste_users', methods=['GET'])
def getAll():
    datas = User.query.filter_by(roles="client").all()
    return jsonify(
        [
        {
        'id': data.id,
        'username': data.username,
        'email': data.email,
        'roles': data.roles,
        'created_at': data.created_at,
        'updated_at': data.updated_at
    } for data in datas]), 200

# # Obtenir un utilisateur par son ID
# @api.route('/getUserById/<int:id>', methods=['GET'])
# def getById(id):
#     user = User.query.get(id)
#     if not user:
#         return jsonify({'msg': "L'utilisateur n'existe pas"}), 404
#     return jsonify({
#         'id': user.id,
#         'username': user.username,
#         'email': user.email,
#         'telephone': user.telephone,
#         'roles': user.roles,
#         'photos': user.photos,
#         'departement': user.departement,
#         'created_at': user.created_at.isoformat() if user.created_at else None,
#         'updated_at': user.updated_at.isoformat() if user.updated_at else None
#     }), 200


# Lite des gérants
# @api.route('/getAllGerants', methods=['GET'])
# def getAllGerants():
#     gerants = User.query.filter(User.roles.contains('Gérant')).all()
#     return jsonify([{
#         'id': gerant.id,
#         'username': gerant.username,
#         'email': gerant.email,
#         'roles': gerant.roles,
#         'created_at': gerant.created_at.isoformat() if gerant.created_at else None,
#         'updated_at': gerant.updated_at.isoformat() if gerant.updated_at else None
#     } for gerant in gerants]), 200

# Nombre des utilisateurs
@api.route('/count_User', methods=['GET'])
def count_User():
    # count = User.query.count()
    count = User.query.filter_by(roles="client").count()
    return jsonify({"count_User": count}), 200

# Le nombre d'utilisateurs par rôle
@api.route('/count_roles', methods=['GET'])
def count_roles():
    admin_count = User.query.filter(User.roles.contains('Admin')).count()
    manager_count = User.query.filter(User.roles.contains('Manager')).count()
    employee_count = User.query.filter(User.roles.contains('Employé')).count()
    return jsonify({
        'admin': admin_count,
        'manager': manager_count,
        'employes': employee_count,
    }), 200

