# COFRAP Serverless

[![OpenFaaS](https://img.shields.io/badge/OpenFaaS-Serverless-blue.svg)](https://www.openfaas.com/)
[![Python](https://img.shields.io/badge/Python-3.x-green.svg)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Description

COFRAP Serverless is a modern authentication application built with OpenFaaS, offering a secure registration and login system with two-factor authentication (2FA). The project uses a serverless architecture for optimal scalability and simplified resource management.

## 🚀 Features

- ✨ **Serverless architecture**: based on OpenFaaS for automatic scalability
- 🔐 **Secure authentication**: Login system with secure password generation
- 📱 **2FA authentication**: Full support for two-factor authentication
- 🗄️ **PostgreSQL database**: Secure storage of user data
- 🎨 **Modern user interface**: responsive frontend with Pico CSS framework
- 🐳 **Containerization** : Docker support for simplified deployment

## 🏗️ Architecture

The project is organized into three main parts:

```
cofrap-serverless/
├── backend/
│   ├── openfaas/          # Functions serverless
│   │   ├── auth-user/     # User authentication
│   │   ├── generate-2fa/  # 2FA code generation
│   │   └── generate-password/ # Password generation
│   ├── sql/               # Database scripts
│   └── vagrant/           # Infrastructure configuration
├── frontend/              # User interface
│   ├── css/              # Custom styles
│   ├── js/               # JavaScript Scripts
│   └── lib/              # External libs
└── docs/                 # Documentations
```

## 📋 Requirements

- **OpenFaaS CLI** : For deploying functions
- **Kubernetes** : Cluster for running OpenFaaS
- **PostgreSQL** : Database (can be deployed on Kubernetes)
- **Docker** : For building images
- **Python 3.x** : For developing functions

## 🛠️ Installation

### 1. Environment configuration

```bash
# Clone the repository
git clone https://github.com/Ahmosys/cofrap-serverless.git
cd cofrap-serverless
```

### 2. Database deployment

```bash
# Use the SQL initialization script
kubectl apply -f backend/sql/init.sql
```

### 3. Secrets configuration

```bash
# Create OpenFaaS secrets
faas-cli secret create postgres-password --from-literal="your-db-password"
faas-cli secret create mfa-key --from-literal="your-mfa-secret-key"
```

### 4. Deploy functions

```bash
# Navigate to the OpenFaaS folder
cd backend/openfaas

# Build and deploy all functions
faas-cli up -f stack.yaml
```

### 5. Frontend deployment

```bash
# Building the frontend Docker image
cd frontend
docker build -t cofrap-frontend .

# Or serve static files directly
python -m http.server 8000
```

## 🔧 Configuration

### Environment variables

OpenFaaS functions use the following environment variables:

- `DB_NAME`: Database name (default: “cofrap”)
- `DB_USER`: Database user (default: “cofrap”)
- `DB_HOST`: Database host
- `DB_PORT`: Database port (default: 5432)

### OpenFaaS Gateway

Modify the gateway URL in `stack.yaml` :

```yaml
provider:
  gateway: http://your-openfaas-gateway:port
```

## 🌐 API Endpoints

### Available functions

| Function | Endpoint | Description |
|----------|----------|-------------|
| `generate-password` | `/function/generate-password` | Generates a secure password for a user and return a QR code |
| `generate-2fa` | `/function/generate-2fa` | Generates a 2FA secret for an existing user and returns the QR code |
| `auth-user` | `/function/auth-user` | Authenticates a user with login / password / 2FA code |

### Usage

```bash
# Create a user account
curl -X POST http://gateway/function/generate-password \
  -H "Content-Type: text/plain" \
  --data "testuser"

# Generate a 2FA code
curl -X POST http://gateway/function/generate-2fa \
  -H "Content-Type: text/plain" \
  --data "testuser"

# Authenticate a user
curl -X POST http://gateway/function/auth-user \
  -H "Content-Type: text/plain" \
  --data "testuser,password,otp-code"
```

## 🎨 User interface

The user interface includes :

- **index.html**: Registration page
- **login.html**: Login page
- **auth-success.html**: Authentication confirmation page

### Frontend features

- User registration form
- 2FA QR code generation and display
- Login interface with 2FA support
- Responsive design with Pico CSS

##  🎨 Frontend Deployment

### 🐳 Docker Deploy

```bash
cd frontend
docker build -t cofrap-frontend .
docker run -p 8080:80 cofrap-frontend
```
### ☸️ Kubernetes Deploy 

The project can also be deployed in a local or remote Kubernetes environment. In our case, we used K3S on a virtualized architecture, with a mono-master cluster configuration and a worker node. 
The frontend was containerized with NGINX (see Docker section) and deployed in Kubernetes via the following files:

- `frontend-deployment.yaml` : describes the pod and allocated resources
- `frontend-service.yaml` : exposes the service on a fixed NodePort

```bash
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

By default, the service is exposed on port 31111 :
```http
http://<node-ip>:31111
```
See the `frontend/k8s/` folder for access to YAML files.

### Functions

Functions are automatically containerized by OpenFaaS during deployment.

## 📊 Monitoring

OpenFaaS provides integrated metrics accessible via :

- OpenFaaS web interface: `http://gateway/ui/`
- Prometheus metrics: `http://gateway/metrics`

## 🔒 Security

- Database hashed passwords with [Bcrypt](https://pypi.org/project/bcrypt/) and 2FA secrets with [Fernet](https://cryptography.io/en/latest/fernet/) (symmetric encryption)
- 2FA authentication with TOTP
- Secrets managed via OpenFaaS
- Secure communication between components

## 🤝 Contribute

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to your branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have any questions or problems :

1. Consult the [documentation](docs/)
2. Open an [issue](https://github.com/Ahmosys/cofrap-serverless/issues)
3. Contact the development team

## 🔗 Useful links

- [OpenFaaS Documentation](https://docs.openfaas.com/)
- [Pico CSS Framework](https://picocss.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

*Developed with ❤️ by the COFRAP team*.
<br>
@ahmosys (H.R), @MasWap (L.L), @ys8o (B.G), @louisalr (L.A)
