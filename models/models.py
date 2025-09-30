from datetime import datetime
from db import db
import json
from utils.auth import hash_password
from sqlalchemy.dialects.postgresql import JSONB

def create_admin_user():
    username = "admin"
    email = "admin@example.com"
    password = "admin123"

    # Vérifie si l’utilisateur existe déjà
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("L'utilisateur admin existe déjà.")
        return

    # Création d’un nouvel utilisateur avec mot de passe hashé
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    print("Utilisateur admin créé avec succès.")

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.String(8), default="client")
    cvs = db.relationship('Cv', backref='users', lazy=True)
    paiements = db.relationship('Paiement', backref='users', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Cv(db.Model):
    __tablename__ = 'cvs'
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    models_cv_id = db.Column(db.Integer, db.ForeignKey('models_cv.id'), nullable=False)
    cvData = db.Column(JSONB) # Contenu complet du CV en JSON"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Model_cv(db.Model):
    __tablename__ = 'models_cv'
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(20), nullable=False)
    images = db.Column(db.String(120), unique=True, nullable=False)
    statut = db.Column(db.String(10), nullable=False)
    cvs = db.relationship('Cv', backref='models_cv', lazy=True)
    paiements = db.relationship('Paiement', backref='models_cv', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Paiement(db.Model):
    __tablename__ = 'paiements'
    id = db.Column(db.Integer, primary_key=True)

    # Lien vers l'utilisateur qui a fait le paiement
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Lien vers le modèle de CV acheté
    models_cv_id = db.Column(db.Integer, db.ForeignKey('models_cv.id'), nullable=False)
    
    # # Lien vers le CV payé
    # cv_id = db.Column(db.Integer, db.ForeignKey('cvs.id'), nullable=False)
    # cv = db.relationship('Cv', backref='paiements', lazy=True)

    # Informations de paiement
    # status = db.Column(db.String(20), nullable=False, default="En attente")
    amount = db.Column(db.Integer, nullable=False)   # ex : 1000 FCFA
    currency = db.Column(db.String(5), nullable=False)  # ex : "XOF"
    description = db.Column(db.String(100), nullable=False)
    transaction_id = db.Column(db.String(120), unique=True, nullable=True)  # ID retourné par CinetPay
    status = db.Column(db.String(20), default="PENDING")  # PENDING, SUCCESS, FAILED
    channels = db.Column(db.String(15), nullable=False)
    mode_paiement = db.Column(db.String(50), nullable=True)  # Orange Money, MTN, Wave...
    cpm_trans_date = db.Column(db.String(50), nullable=True)  # Orange Money, MTN, Wave...
    cel_phone_num = db.Column(db.String(50), nullable=True)  # Orange Money, MTN, Wave...
    cpm_phone_prefixe = db.Column(db.String(50), nullable=True)  # Orange Money, MTN, Wave...
    cpm_error_message = db.Column(db.String(50), nullable=True)  # Orange Money, MTN, Wave...
    cpm_site_id = db.Column(db.String(50), nullable=True)  # Orange Money, MTN, Wave...

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# class Abonnements(db.Model):
#     __tablename__ = 'abonnements'
#     id = db.Column(db.Integer, primary_key=True)
#     type_abonnement = db.Column(db.String(15), nullable=False)
#     montant = db.Column(db.Integer, nullable=False)
#     dateDebut = db.Column(db.DateTime, nullable=False)
#     dateFin = db.Column(db.DateTime, nullable=False)
#     statut = db.Column(db.String(15), nullable=False)
#     restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
#     paiements = db.relationship('Paiements', backref='abonnements', lazy=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# class Paiements(db.Model):
#     __tablename__ = 'paiements'
#     id = db.Column(db.Integer, primary_key=True)
#     transaction_id = db.Column(db.String(250), nullable=False, unique=True)
#     amount = db.Column(db.Integer, nullable=False)
#     currency = db.Column(db.String(5), nullable=False)
#     description = db.Column(db.String(100), nullable=False)
#     channels = db.Column(db.String(15), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="En attente")
#     mode_paiement = db.Column(db.String(50), default="CinetPay")
#     restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
#     abonnement_id = db.Column(db.Integer, db.ForeignKey('abonnements.id'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    