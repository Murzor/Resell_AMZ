# API Arbitrage Amazon - Backend

API FastAPI mono-utilisateur pour un outil d'arbitrage Amazon.

## Structure

- `app/` - Code de l'application
  - `api/routes/` - Routes API (auth, settings, search, product, calc, lists, alerts)
  - `core/` - Configuration, base de données, sécurité
  - `models/` - Modèles SQLAlchemy
  - `schemas/` - Schémas Pydantic
  - `workers/` - Workers RQ pour les tâches asynchrones
- `alembic/` - Migrations de base de données
- `tests/` - Tests pytest
- `scripts/` - Scripts utilitaires (seed, etc.)

## Installation

### Avec Docker Compose (recommandé)

```bash
# Copier le fichier d'environnement
cp env.example .env

# Démarrer les services
make dev

# Appliquer les migrations
make migrate

# Initialiser les données
make seed
```

### Développement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Installer Playwright
playwright install chromium

# Configurer la base de données
# Modifier DATABASE_URL dans .env

# Appliquer les migrations
alembic upgrade head

# Lancer l'API
uvicorn app.main:app --reload
```

## Utilisation

### API

L'API est disponible sur `http://localhost:8000`

Documentation interactive: `http://localhost:8000/docs`

### Workers

Les workers RQ sont lancés automatiquement avec Docker Compose. Pour les lancer manuellement:

```bash
rq worker --url redis://localhost:6379/0 default
```

### Base de données

Adminer est disponible sur `http://localhost:8080`

- Serveur: `postgres`
- Utilisateur: `arbitrage_user`
- Mot de passe: `arbitrage_pass`
- Base de données: `arbitrage_db`

## Commandes Make

- `make dev` - Démarrer tous les services
- `make migrate` - Appliquer les migrations
- `make migrate-create MESSAGE="description"` - Créer une nouvelle migration
- `make seed` - Initialiser les données
- `make test` - Lancer les tests
- `make lint` - Vérifier le code
- `make format` - Formater le code
- `make clean` - Supprimer les conteneurs et volumes

## Endpoints API

### Auth
- `POST /api/auth/login` - Connexion (mot de passe depuis .env)

### Settings
- `GET /api/settings` - Liste des paramètres
- `GET /api/settings/{key}` - Récupérer un paramètre
- `POST /api/settings` - Créer un paramètre
- `PUT /api/settings/{key}` - Mettre à jour un paramètre

### Search
- `GET /api/search` - Recherche paginée avec filtres (ROI%, marge€, BSR, etc.)

### Product
- `GET /api/product/{asin}` - Détails d'un produit

### Calc
- `POST /api/calc` - Calculer landed_cost, marge€, ROI%

### Lists
- `GET /api/lists` - Liste des listes
- `POST /api/lists` - Créer une liste
- `GET /api/lists/{id}/export/csv` - Exporter en CSV
- `POST /api/lists/{id}/export/google-sheets` - Exporter vers Google Sheets

### Alerts
- `GET /api/alerts` - Liste des alertes
- `POST /api/alerts` - Créer une alerte
- `POST /api/alerts/{id}/run` - Exécuter une alerte

## Tests

```bash
make test
```

Les tests incluent:
- Tests de calcul (calc)
- Tests de scraper (dry-run)
- Tests d'authentification

## Configuration

Variables d'environnement (voir `env.example`):

- `DATABASE_URL` - URL de connexion PostgreSQL
- `SECRET_KEY` - Clé secrète pour JWT
- `ADMIN_PASSWORD` - Mot de passe admin
- `REDIS_URL` - URL Redis
- `CORS_ORIGINS` - Origines CORS autorisées
- `SENTRY_DSN` - DSN Sentry (optionnel)

