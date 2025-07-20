from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from flask_cors import CORS

tokens_bp = Blueprint('tokens', __name__)
CORS(tokens_bp)

# Token user -- super Admin
@tokens_bp.route('/tokens/users', methods=['GET'])
@jwt_required()
def get_token_users():
    try:
        auth_header = request.headers.get('Authorization', '')
        
        # Validation améliorée du header
        if not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Format de token invalide. Utilisez: Bearer <token>'}), 401

        # Extraction sécurisée du token
        token = auth_header.split('Bearer ')[1].strip()
        if not token:
            return jsonify({'message': 'Token vide détecté'}), 401

        # Récupération de l'identité
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        # Réponse sécurisée
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': user.roles,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            # Ne renvoyez pas le token existant pour des raisons de sécurité
        }

        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur dans get_token: {str(e)}")
        return jsonify({'message': 'Erreur serveur'}), 500
