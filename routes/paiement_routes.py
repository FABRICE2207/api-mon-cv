from flask import Blueprint, request, jsonify
from models import db, Paiement
import os
import requests
import uuid
from datetime import datetime, timedelta
from models.models import Cv
from sqlalchemy import func

api = Blueprint("paiements_api", __name__)

# Clé API de paiement
CINETPAY_APIKEY = os.getenv("CINETPAY_APIKEY")

# Site id
CINETPAY_SITE_ID = os.getenv("CINETPAY_SITE_ID")

# Notification
CINETPAY_NOTIFY_URL = os.getenv("CINETPAY_NOTIFY_URL")

# Retourne url
CINETPAY_RETURN_URL = os.getenv("CINETPAY_RETURN_URL")

# Route paiement
@api.route("/payments_init", methods=["POST"])
def initier_paiement():
    data = request.get_json()
    montant = data.get("montant")
    users_id = data.get("users_id")
    models_cv_id = data.get("models_cv_id")

    # if not all([montant, abonnement_id, restaurant_id]):
    #     return jsonify({"error": "Données incomplètes"}), 400

    # abonnement = Abonnements.query.filter_by(id=abonnement_id, restaurant_id=restaurant_id).first()
    # if not abonnement:
    #     return jsonify({"error": "Abonnement introuvable"}), 404

    transaction_id = f"PMT-CV-{uuid.uuid4().hex[:20]}".upper()

    url = "https://api-checkout.cinetpay.com/v2/payment"
    

    payload = {
        "apikey": CINETPAY_APIKEY, # APIKEY de cinetpay
        "site_id": CINETPAY_SITE_ID, # ID du site de cinetpay
        "transaction_id": transaction_id,
        "amount": montant,  # montant en chiffre entier
        "currency": "XOF",
        "description":"Paiement pour modèle CV",
        "notify_url": CINETPAY_NOTIFY_URL,  
        "return_url": CINETPAY_RETURN_URL,      
        "channels": "ALL",
        # "return_url": "http://localhost:3000/payment-success",
        # "notify_url": "http://localhost:5000/api/paiements/payments/callback"
        # "invoice_data":{
        #     "Reste à payer":"25 000fr",
        #     "Matricule":"24OPO25",
        #     "Annee-scolaire":"2020-2021"
        # }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 💳 Appel vers CinetPay
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        print(result)

        if result["code"] == '201' and result["data"]["payment_url"]:
            # Enregistrer le paiement en base
            paiement = Paiement(
                transaction_id=transaction_id,
                amount=montant,
                currency="XOF",
                description=payload["description"],
                # notify_url=payload["notify_url"],
                # return_url=payload["return_url"],
                channels="ALL",
                status="PENDING",
                users_id=users_id,
                models_cv_id=models_cv_id,
            )

            db.session.add(paiement)
            db.session.commit()

            return jsonify(result), 201
        else:
            return jsonify({
                "error": "Échec de la création du paiement",
                "details": result
            }), 400

    except Exception as e:
        return jsonify({"error": "Erreur serveur", "message": str(e)}), 500

# Callback CinetPay (notification serveur à serveur)
# @api.route("/payments/callback", methods=["POST", "GET"])
# def callback_paiement():
#     if request.method == "GET":
#         return "CinetPay Callback Endpoint", 200
#     data = request.json
#     transaction_id = data.get("cpm_trans_id")
#     status = data.get("status")

#     paiement = Paiement.query.filter_by(transaction_id=transaction_id).first()
#     paiement.status = "SUCCESS"
#     paiement.cpm_trans_date = data.get("cpm_trans_date")
#     paiement.cel_phone_num = data.get("cel_phone_num")
#     paiement.cpm_phone_prefixe = data.get("cpm_phone_prefixe")
#     paiement.cpm_error_message = data.get("cpm_error_message")
#     paiement.cpm_site_id = data.get("cpm_site_id")


#     if not paiement:
#         return jsonify({"error": "Transaction inconnue"}), 404

#     # vérification transaction
#     url = "https://api-checkout.cinetpay.com/v2/payment/check"
    

#     payload = {
#         "apikey": CINETPAY_APIKEY, # APIKEY de cinetpay
#         "site_id": CINETPAY_SITE_ID, # ID du site de cinetpay
#         "transaction_id": transaction_id,
#     }

#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"
#     }

#     try:
#         response = requests.post(url, data=payload, headers=headers)
#         result = response.json()
#         print("Vérification CinetPay:", result)
#         paiement.mode_paiement = data.get("payment_method")
#         if result["code"] == '00':
#             # Mise à jour statut
#             paiement.status = "SUCCESS" 
#             paiement.updated_at = datetime.utcnow()
#             db.session.commit()

#             return jsonify({"message": "Statut mis à jour", "statut": paiement.status}), 200

#     except Exception as e:
#         return jsonify({"error": "Erreur serveur lors de la vérification", "message": str(e)}), 500

# Callback CinetPay (notification serveur à serveur)
@api.route("/payments/callback", methods=["POST", "GET"])
def callback_paiement():
    if request.method == "GET":
        return "CinetPay Callback Endpoint", 200

    data = request.form
    transaction_id = data.get("cpm_trans_id")
    status = data.get("status")

    paiement = Paiement.query.filter_by(transaction_id=transaction_id).first()
    if not paiement:
        return jsonify({"error": "Transaction inconnue"}), 404

    # Mettre à jour infos de base
    paiement.status = "PENDING"
    paiement.cpm_trans_date = data.get("cpm_trans_date")
    paiement.cel_phone_num = data.get("cel_phone_num")
    paiement.cpm_phone_prefixe = data.get("cpm_phone_prefixe")
    paiement.cpm_error_message = data.get("cpm_error_message")
    paiement.cpm_site_id = data.get("cpm_site_id")

    # Vérification transaction chez CinetPay
    url = "https://api-checkout.cinetpay.com/v2/payment/check"
    payload = {
        "apikey": CINETPAY_APIKEY,
        "site_id": CINETPAY_SITE_ID,
        "transaction_id": transaction_id,
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)  # ✅ envoi x-www-form-urlencoded
        result = response.json()
        print("Vérification CinetPay:", result)

        paiement.mode_paiement = data.get("payment_method")

        if result.get("code") == "00":
            # Mise à jour statut
            paiement.status = "SUCCESS"
            # paiement.expire_at=datetime.utcnow() + timedelta(minutes=2) # 2min d'accès au modèle
            paiement.expire_at = datetime.utcnow() + timedelta(hours=24) # 24h d'accès au modèle
        else:
            paiement.status = "FAILED"

        db.session.commit()

        return jsonify({"message": "Statut mis à jour", "statut": paiement.status}), 200

    except Exception as e:
        return jsonify({"error": "Erreur serveur lors de la vérification", "message": str(e)}), 500

    
# # Liste des paiements
@api.route("/liste_paiement", methods=["GET"])
def paiement_liste():
    # Afficher les paiements les plus récents en premiers
    paiements = Paiement.query.order_by(Paiement.created_at.desc()).all()
    return jsonify([
        {
            'transaction_id': paiement.transaction_id,
            'amount': paiement.amount,
            'currency': paiement.currency,
            'description': paiement.description,
            'channels': paiement.channels,
            'status': paiement.status,
            'users': {
                'id': paiement.users_id,
                'username': paiement.users.username,
            },
            'mode_paiement': paiement.mode_paiement,
            'models_cv': {
                'id': paiement.models_cv_id,
                'libelle': paiement.models_cv.libelle,
            },
            'created_at': paiement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': paiement.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(paiements), # format lisible
        } for paiement in paiements
    ]), 200

from datetime import datetime

@api.route("/payments_success/<int:user_id>/models_cv", methods=["GET"])
def get_success_models_by_user(user_id):
    try:
        now = datetime.utcnow()

        # Paiements SUCCESS non expirés
        paiements_success = Paiement.query.filter(
            Paiement.status == "SUCCESS",
            Paiement.users_id == user_id,
            Paiement.expire_at > now  # ⏳ expiration pas encore atteinte
        ).all()

        # Extraire les IDs uniques
        models_ids = list({paiement.models_cv_id for paiement in paiements_success})

        return jsonify({
            "success": True,
            "user_id": user_id,
            "count": len(models_ids),
            "models_cv_ids": models_ids,
            "expire_dates": {p.models_cv_id: p.expire_at.isoformat() for p in paiements_success}
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la récupération : {str(e)}"
        }), 500

# Montant total des paiements réussis
@api.route("/dashboard/statistic", methods=["GET"])
def dashboard_stats():
    try:
        # Total montant en caisse (paiements réussis)
        total_montant = db.session.query(func.sum(Paiement.amount)).filter(Paiement.status == "SUCCESS").scalar() or 0

        # Nombre de Cv dont le paiement est pending
        nb_cv_pending = db.session.query(Paiement).filter(Paiement.status == "PENDING").count()

        # Nombre de CV téléchargés (paiements réussis)
        nb_cv_telecharges = db.session.query(Paiement).filter(Paiement.status == "SUCCESS").count()

        # Nombre de CV créés (modèles ou CVs selon ton modèle Cv)
        nb_cv_crees = db.session.query(Cv).count()

        return jsonify({
            "success": True,
            "total_montant": total_montant,
            "nb_cv_pending": nb_cv_pending,
            "nb_cv_telecharges": nb_cv_telecharges,
            "nb_cv_crees": nb_cv_crees
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors du calcul des stats : {str(e)}"
        }), 500
