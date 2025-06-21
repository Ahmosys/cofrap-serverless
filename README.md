# COFRAP Serverless

[![OpenFaaS](https://img.shields.io/badge/OpenFaaS-Serverless-blue.svg)](https://www.openfaas.com/)
[![Python](https://img.shields.io/badge/Python-3.x-green.svg)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Description

COFRAP Serverless est une application d'authentification moderne construite avec OpenFaaS, offrant un système d'inscription et de connexion sécurisé avec authentification à deux facteurs (2FA). Le projet utilise une architecture serverless pour une scalabilité optimale et une gestion simplifiée des ressources.

## 🚀 Fonctionnalités

- ✨ **Architecture Serverless** : Basée sur OpenFaaS pour une scalabilité automatique
- 🔐 **Authentification sécurisée** : Système de connexion avec génération de mots de passe sécurisés
- 📱 **Authentification 2FA** : Support complet de l'authentification à deux facteurs
- 🗄️ **Base de données PostgreSQL** : Stockage sécurisé des données utilisateur
- 🎨 **Interface utilisateur moderne** : Frontend responsive avec framework CSS Pico
- 🐳 **Containerisation** : Support Docker pour un déploiement simplifié

## 🏗️ Architecture

Le projet est organisé en trois parties principales :

```
cofrap-serverless/
├── backend/
│   ├── openfaas/          # Functions serverless
│   │   ├── auth-user/     # Authentification utilisateur
│   │   ├── generate-2fa/  # Génération codes 2FA
│   │   └── generate-password/ # Génération mots de passe
│   ├── sql/               # Scripts base de données
│   └── vagrant/           # Configuration infrastructure
├── frontend/              # Interface utilisateur
│   ├── css/              # Styles personnalisés
│   ├── js/               # Scripts JavaScript
│   └── lib/              # Bibliothèques externes
└── docs/                 # Documentation
```

## 📋 Prérequis

- **OpenFaaS CLI** : Pour le déploiement des functions
- **Kubernetes** : Cluster pour l'exécution d'OpenFaaS
- **PostgreSQL** : Base de données (peut être déployée sur Kubernetes)
- **Docker** : Pour la construction des images
- **Python 3.x** : Pour le développement des functions

## 🛠️ Installation

### 1. Configuration de l'environnement

```bash
# Cloner le repository
git clone https://github.com/Ahmosys/cofrap-serverless.git
cd cofrap-serverless
```

### 2. Déploiement de la base de données

```bash
# Utiliser le script SQL d'initialisation
kubectl apply -f backend/sql/init.sql
```

### 3. Configuration des secrets

```bash
# Créer les secrets OpenFaaS
faas-cli secret create postgres-password --from-literal="your-db-password"
faas-cli secret create mfa-key --from-literal="your-mfa-secret-key"
```

### 4. Déploiement des functions

```bash
# Naviguer vers le dossier OpenFaaS
cd backend/openfaas

# Construire et déployer toutes les functions
faas-cli up -f stack.yaml
```

### 5. Déploiement du frontend

```bash
# Construire l'image Docker du frontend
cd frontend
docker build -t cofrap-frontend .

# Ou servir directement les fichiers statiques
python -m http.server 8000
```

## 🔧 Configuration

### Variables d'environnement

Les functions OpenFaaS utilisent les variables d'environnement suivantes :

- `DB_NAME` : Nom de la base de données (défaut: "cofrap")
- `DB_USER` : Utilisateur de la base de données (défaut: "cofrap")
- `DB_HOST` : Hôte de la base de données
- `DB_PORT` : Port de la base de données (défaut: 5432)

### Gateway OpenFaaS

Modifiez l'URL du gateway dans `stack.yaml` :

```yaml
provider:
  gateway: http://your-openfaas-gateway:port
```

## 🌐 API Endpoints

### Functions disponibles

| Function | Endpoint | Description |
|----------|----------|-------------|
| `generate-password` | `/function/generate-password` | Génère un mot de passe sécurisé pour un utilisateur |
| `generate-2fa` | `/function/generate-2fa` | Génère un secret 2FA et retourne le QR code |
| `auth-user` | `/function/auth-user` | Authentifie un utilisateur avec login/password/2FA |

### Utilisation

```bash
# Créer un compte utilisateur
curl -X POST http://gateway/function/generate-password \
  -d '{"username": "testuser"}'

# Générer un code 2FA
curl -X POST http://gateway/function/generate-2fa \
  -d '{"username": "testuser"}'

# Authentifier un utilisateur
curl -X POST http://gateway/function/auth-user \
  -d '{"username": "testuser", "password": "password", "token": "123456"}'
```

## 🎨 Interface utilisateur

L'interface utilisateur comprend :

- **index.html** : Page d'inscription
- **login.html** : Page de connexion
- **auth-success.html** : Page de confirmation d'authentification

### Fonctionnalités frontend

- Formulaire d'inscription utilisateur
- Génération et affichage du QR code 2FA
- Interface de connexion avec support 2FA
- Design responsive avec Pico CSS

## 🐳 Docker

### Frontend

```bash
cd frontend
docker build -t cofrap-frontend .
docker run -p 8080:80 cofrap-frontend
```

### Functions

Les functions sont automatiquement containerisées par OpenFaaS lors du déploiement.

## 📊 Monitoring

OpenFaaS fournit des métriques intégrées accessibles via :

- Interface web OpenFaaS : `http://gateway/ui/`
- Métriques Prometheus : `http://gateway/metrics`

## 🔒 Sécurité

- Mots de passe hashés en base de données
- Authentification 2FA avec TOTP
- Secrets gérés via OpenFaaS
- Communication sécurisée entre components

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche feature (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙋‍♂️ Support

Pour toute question ou problème :

1. Consultez la [documentation](docs/)
2. Ouvrez une [issue](https://github.com/Ahmosys/cofrap-serverless/issues)
3. Contactez l'équipe de développement

## 🔗 Liens utiles

- [Documentation OpenFaaS](https://docs.openfaas.com/)
- [Pico CSS Framework](https://picocss.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

*Développé avec ❤️ par l'équipe COFRAP*
