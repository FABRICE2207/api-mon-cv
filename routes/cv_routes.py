
# ============================
# 📁 routes.py — API CRUD + Auth
# ============================
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from models import db, Cv
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

api = Blueprint('cvs_api', __name__)

# Ajouter un nouveau CV
# @api.route('/add_new_cv', methods=['POST'])
# @jwt_required()
# def add_new_cv():
#     try:
#         current_user_id = get_jwt_identity()
#         data = request.get_json()

#         required_fields = ['models_cv_id', 'users_id', 'cvData']

#         missing_fields = [field for field in required_fields if field not in data or data[field] in [None, ""]]
#         if missing_fields:
#             return jsonify({"error": f"Champs manquants : {', '.join(missing_fields)}"}), 400

#         # Conversion du contenu de l'infos du cv
#         cvData = data['cvData']
#         if isinstance(cvData, str):
#             try:
#                 cvData = json.loads(cvData)
#             except json.JSONDecodeError:
#                 return jsonify({"error": "cvDataJSON invalide"}), 400

#         # Création du CV (la conversion JSON est gérée automatiquement par le modèle)
#         new_cv = Cv(
#             cvData=data['cvData'],  # Peut être dict ou string JSON
#             users_id=current_user_id,
#             models_cv_id=data.get('models_cv_id')
#         )

#         db.session.add(new_cv)
#         db.session.commit()

#         return jsonify({
#             "message": "CV créé avec succès",
#             "cv_id": new_cv.id,
#             "cvData": new_cv.cvData,
#             "users_id": current_user_id
#         }), 201

#     except ValueError as e:
#         db.session.rollback()
#         return jsonify({"error": "Données JSON invalides", "details": str(e)}), 400
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": "Erreur serveur", "details": str(e)}), 500

@api.route('/add_new_cv', methods=['POST'])
@jwt_required()
def add_new_cv():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validation des champs
        required_fields = ['models_cv_id', 'users_id', 'cvData']
        missing_fields = [field for field in required_fields if field not in data or data[field] in [None, ""]]
        if missing_fields:
            return jsonify({"error": f"Champs manquants : {', '.join(missing_fields)}"}), 400

        # Vérification si un CV identique existe déjà
        existing_cv = Cv.query.filter_by(
            users_id=current_user_id,
            models_cv_id=data['models_cv_id'],
            cvData=data['cvData']  # Comparaison directe du JSON
        ).first()

        if existing_cv:
            return jsonify({
                "message": "Désolé, le titre du CV existe déjà."
            }), 409  # 409 Conflict

        # Création du nouveau CV
        new_cv = Cv(
            cvData=data['cvData'],
            users_id=current_user_id,
            models_cv_id=data['models_cv_id']
        )

        db.session.add(new_cv)
        db.session.commit()

        return jsonify({
            "message": "CV créé avec succès",
            "cv_id": new_cv.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Ajouter la photo de profil 
@api.route("/photo_user_cv", methods=["POST"])
def upload_photo():
    # data = request.get_json()
    
    # print("Fichier reçu:", data)
    
    if "photos" not in request.files:
        return jsonify({"error": "Pas de fichier 'photo' dans la requête"}), 400

    file = request.files["photos"]

    if file.filename == "":
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Retourne le nom du fichier pour stockage en base
        return jsonify({"filename": filename}), 201

    return jsonify({"error": "Type de fichier non autorisé"}), 400

# Afficher la photo de profil sur le cv
@api.route('/get_cv_photo/<filename>', methods=['GET'])
def get_photo_cv(filename):
  return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Supprimer une photo
@api.route('/delete_photo/<filename>', methods=['DELETE'])
def delete_photo(filename):
    # Vérifie si le nom du fichier est fourni
    print("Nom du fichier reçu:", filename)
    if not filename:
        return jsonify({"error": "Nom de fichier manquant"}), 400

    # Chemin absolu du fichier à supprimer
    file_path = os.path.join(current_app.root_path, 'static/uploads', filename)

    # Suppression du fichier s'il existe
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Photo supprimée avec succès")
        return jsonify({"message": "Photo supprimée"}), 200
    else:
        return jsonify({"error": "Fichier introuvable"}), 404



# Liste des Cvs
@api.route('/liste_cvs', methods=['GET'])
def list_cvs():
    cvs = Cv.query.all()
    return jsonify([{
        "id": cv.id,
        "users": {
            "username": cv.users.username,    
        },
        "cvData": cv.cvData,
        "models_cv_id": cv.models_cv_id,
        
    } for cv in cvs])

@api.route('/Cvs/<int:id>', methods=['GET'])
@jwt_required()
def get_Cv(id):
    Cv = Cv.query.get_or_404(id)
    return jsonify({
        "id": Cv.id,
        "cvData": Cv.Cv,
        "date_creation": Cv.date_creation.isoformat()
    })

# Lister les CV d'un utilisateur
@api.route('/liste_cv/user/<int:users_id>', methods=['GET'])
def get_user_Cvs(users_id):
    # liste des cv par ordre décroissant (plus récent en premier)
    cvs = cvs = Cv.query.filter_by(users_id=users_id).order_by(Cv.id.desc()).all()
    nbre_cv = len(cvs)
    return jsonify([{
        "id": cv.id,
        "users": {
            "id": cv.users.id,
            "username": cv.users.username,    
        },
        "cvData": cv.cvData,
        "models_cv_id": cv.models_cv_id,
        "nbre_cv":  nbre_cv,
        "created_at": cv.created_at
    } for cv in cvs])


# Mise à jour d'un CV
@api.route('/Cvs/<int:id>', methods=['PUT'])
@jwt_required()
def update_Cv(id):
    Cv = Cv.query.get_or_404(id)
    data = request.get_json()
    if not data or 'titre' not in data or 'cvData' not in data:
        return jsonify({"error": "Titre ou cvData manquant"}), 400
    Cv.titre = data['titre']
    Cv.cvData = data['cvData']
    db.session.commit()
    return jsonify({"message": "Cv mis à jour"})

# Supprimer un CV
@api.route('/Cvs/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_Cv(id):
    Cv = Cv.query.get_or_404(id)
    db.session.delete(Cv)
    db.session.commit()
    return jsonify({"message": "Cv supprimé"})