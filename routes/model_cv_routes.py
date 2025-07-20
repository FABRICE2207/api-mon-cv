from flask import Blueprint, request, jsonify, current_app, send_from_directory
from models import db, Model_cv, Cv
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date
from flask_jwt_extended  import jwt_required
from sqlalchemy import func

api = Blueprint("model_cv_api", __name__)

#Configuration pour le téléchargement de photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ajouter un model
@api.route("/add_model_cv", methods=["POST"])
def add_model_cv():
    try:
        libelle = request.form.get('libelle')
        file_image = request.files.get('images')
        statut = request.form.get('statut')

        print(libelle, file_image, statut)

        if not all([libelle, file_image, statut]):
            return jsonify({'error': 'Veuillez remplir tous les champs obligatoires'}), 400

        if not allowed_file(file_image.filename):
            return jsonify({'error': "Type de fichier non autorisé. Formats acceptés: PNG, JPG, JPEG, WEBP"}), 400

        # Renommer l'image pour éviter les collisions
        filename = secure_filename(file_image.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file_image.save(file_path)

        new_models = Model_cv(
            libelle=libelle,
            statut=statut,
            images=filename,
        )
        db.session.add(new_models)
        db.session.commit()

        return jsonify({
            'message': 'Modèle ajouté avec succès',
            'modele': {
                'id': new_models.id,
                'libelle': new_models.libelle,
                'statut': new_models.statut,
                'images': new_models.images,
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la création du modèle: {str(e)}")
        return jsonify({'error': 'Une erreur interne est survenue.'}), 500


# Afficher les images 
@api.route('/modele_cv/<filename>', methods=['GET'])
def uploaded_file(filename):
  return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Afficher les models
@api.route("/liste_model_cv", methods=["GET"])
def get_all_models_cv():
    models = Model_cv.query.order_by(Model_cv.created_at.asc()).all()
    return jsonify([
       {
            "id": model.id,
            "libelle": model.libelle,
            "statut": model.statut,
            "images": model.images,
        }
        for model in models
    ]), 200

# Afficher les models de cv activés
@api.route("/liste_model_cv_actives", methods=["GET"])
def get_all_models_cv_actives():
    models_actif = Model_cv.query.filter_by(statut="Activé").order_by(Model_cv.created_at.asc()).all()

    return jsonify([
       {
            "id": model.id,
            "libelle": model.libelle,
            "statut": model.statut,
            "images": model.images,
        }
        for model in models_actif
    ]), 200

# affichez un seul model
@api.route("/modele_cv/<int:id>", methods=["GET"])
def get_model_cv(id):
    model = Model_cv.query.get_or_404(id)
    if not model:
      return jsonify({"error": "Model CV non trouvé"}), 404
    return jsonify({
          "id": model.id,
          "images": model.images,
      }), 200

@api.route("/image_cv/<int:id>", methods=["GET"])
def get_cv_image(id):
    # 1. Trouver le CV
    cv = Cv.query.get(id)
    if not cv:
        return jsonify({"error": "CV introuvable"}), 404

    # 2. Trouver le modèle de CV associé
    modele = Model_cv.query.get(cv.models_cv_id)
    if not modele:
        return jsonify({"error": "Modèle de CV introuvable"}), 404

    # 3. Récupérer le nom de fichier de l'image
    image_filename = modele.images
    upload_folder = current_app.config['UPLOAD_FOLDER']
    image_path = os.path.join(upload_folder, image_filename)

    if not os.path.exists(image_path):
        return jsonify({"error": "Image introuvable"}), 404

    # 4. Envoyer l’image
    return send_from_directory(upload_folder, image_filename)

# Changer le statut en Activé ou Désactivé
@api.route('/update_statut_modeles/<int:id>', methods=['PUT'])
def update_plat_statut(id):
    try:
        modele = Model_cv.query.get(id)
        if not modele:
            return jsonify({'error': 'Modèle non trouvé'}), 404

        # Alterner le statut
        if modele.statut == "Activé":
            modele.statut = "Désactivé"
        else:
            modele.statut = "Activé"

        db.session.commit()

        return jsonify({
            'message': 'Statut du modèle mis à jour avec succès',
            'id': modele.id,
            'libelle': modele.libelle,
            'statut': modele.statut
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
