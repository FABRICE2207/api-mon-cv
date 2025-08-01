# 🧾 CVBuilder Pro

**Plateforme web fullstack pour créer, gérer et personnaliser des CV professionnels**, avec **Next.js + Tailwind + Redux Toolkit** en frontend, et **Flask + PostgreSQL** en backend.

---

## 🚀 Fonctionnalités clés

- 🔐 Authentification JWT (connexion/inscription)
- 🧑‍💼 Création de CV dynamiques : expériences, formations, langues, compétences…
- 🎨 Choix de modèles de CV (moderne, classique, etc.)
- 🖥️ Aperçu en temps réel pendant la saisie
- 📄 Export des CV au format PDF
- 🧾 Interface d’administration :
  - Gestion des modèles de CV
  - Gestion des utilisateurs
- 🌙 Mode sombre

---

## 🛠️ Stack technique

| Frontend (Next.js)         | Backend (Flask)                     |
|---------------------------|-------------------------------------|
| React 18 + Next.js        | Flask / Flask-RESTful               |
| TailwindCSS               | Flask-JWT-Extended / SQLAlchemy     |
| Redux Toolkit             | Marshmallow / Flask-Migrate         |
| Axios                     | PostgreSQL                          |
| html2canvas + jsPDF       | CORS, dotenv                        |
| shadcn/ui + lucide-react  |                                     |

---

## 📦 Installation complète (fullstack)

### 🔧 Prérequis

- Node.js ≥ 18
- Python ≥ 3.11
- PostgreSQL
- Git

---

### 📁 1. Backend (Flask)

```bash
# Cloner le backend
git clone https://github.com/votre-username/api-cvbuilder.git
cd api-cvbuilder

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d’environnement
cp .env.example .env  # puis modifier avec vos infos

# Initialiser la base de données
flask db init
flask db migrate
flask db upgrade

# Démarrer le serveur
flask run
```

#### Exemple de `.env`

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=postgresql://user:password@localhost/cvbuilder_db
```

---

### 🌐 2. Frontend (Next.js)

```bash
# Cloner le frontend
git clone https://github.com/votre-username/cvbuilder-next.git
cd cvbuilder-next

# Installer les dépendances
npm install

# Démarrer le projet
npm run dev
```

---

## 🧾 Exemple de structure de CV (JSON)

```ts
{
  titre: "Développeur Fullstack",
  description: "Développeur expérimenté avec 4+ ans d'expérience",
  informations_personnelles: {
    username: "Jean Dupont",
    email: "jean@example.com",
    telephone: "+2250707070707",
    adresse: "Abidjan, Côte d'Ivoire",
    linkedin: "https://linkedin.com/in/jeandupont"
  },
  experiences: [
    {
      id: 1,
      entreprise: "TechCorp",
      poste: "Frontend Developer",
      date_debut: "2022-01",
      date_fin: "2023-06",
      missions: [
        { id: 1, missions_details: "Développement de composants React" },
        { id: 2, missions_details: "Amélioration UX avec TailwindCSS" }
      ]
    }
  ],
  formations: [...],
  competences: [...],
  langues: [...],
  certifications: [...],
  centres_interet: [...]
}
```

---

## 📄 Export PDF

- 📷 Génération d’un screenshot DOM via `html2canvas`
- 🧾 Conversion avec `jsPDF`
- 📁 Nom de fichier dynamique selon `username` : `CV_JeanDupont.pdf`

```ts
export interface ExportOptions {
  format: "A4" | "Letter"
  orientation: "portrait" | "landscape"
  quality: "standard" | "high"
  includeColors: boolean
  filename?: string // généré dynamiquement avec le username
}
```

---

## 🧑‍💼 Espace Admin

- 🔍 Liste paginée des utilisateurs
- 🎨 Création et suppression de modèles CV
- 🧹 Activation/désactivation de modèles
- 📊 Vue future des statistiques

---

## 📌 Fonctionnalités à venir

- 📁 Dossiers de candidatures
- 🔗 Partage de CV public (via lien)
- 🎨 Customisation avancée (couleurs, typographies)
- 📊 Dashboard personnel

---

## 🧪 Tests & Debug

- Backend : test via Postman avec JWT
- Frontend : test via navigateur local (`http://localhost:3000`)

---

## 📜 Licence

Projet open-source sous licence MIT.