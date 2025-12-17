# 🎓 AWS Learning Platform

A cloud-native microservices-based learning platform built with FastAPI, Docker, and AWS services.

## 📋 Overview

This platform provides an AI-powered learning experience with document processing, speech synthesis, and interactive quizzes. The system is designed using a microservices architecture deployed on AWS.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (:8000)                       │
│                     (User Management)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Doc Service  │    │ Chat Service │    │ Quiz Service │
│   (:8001)    │    │   (:8005)    │    │   (:8004)    │
└──────┬───────┘    └──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐
│ STT Service  │    │ TTS Service  │
│   (:8002)    │    │   (:8003)    │
└──────────────┘    └──────────────┘
       │                   │
       └─────────┬─────────┘
                 ▼
         ┌─────────────┐
         │    Kafka    │
         │  (Events)   │
         └─────────────┘
```

## 🚀 Services

| Service | Port | Description |
|---------|------|-------------|
| **API Gateway** | 8000 | User registration and authentication |
| **Document Service** | 8001 | Upload and manage documents (S3 storage) |
| **STT Service** | 8002 | Speech-to-Text transcription |
| **TTS Service** | 8003 | Text-to-Speech synthesis |
| **Quiz Service** | 8004 | Generate quizzes from documents |
| **Chat Service** | 8005 | Interactive chat with bot responses |

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (AWS RDS)
- **Message Queue**: Apache Kafka
- **Storage**: AWS S3
- **Secrets**: AWS Secrets Manager
- **Container Registry**: Amazon ECR
- **CI/CD**: AWS CodeBuild & CodePipeline
- **Containerization**: Docker & Docker Compose

## 📦 Prerequisites

- Docker & Docker Compose
- AWS CLI configured with credentials
- Python 3.11+

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=your_session_token
AWS_DEFAULT_REGION=us-east-1
```

## 🚀 Quick Start

### Local Development with Docker Compose

```bash
# Clone the repository
git clone https://github.com/Joeee14/aws-learning-platform.git
cd aws-learning-platform

# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Access the Services

- API Gateway: http://localhost:8000
- Document Service: http://localhost:8001
- STT Service: http://localhost:8002
- TTS Service: http://localhost:8003
- Quiz Service: http://localhost:8004
- Chat Service: http://localhost:8005

## 📡 API Endpoints

### API Gateway
```
POST /api/users/register
Body: { "username": "john", "email": "john@example.com" }
```

### Document Service
```
POST /api/documents/upload
Form: file (multipart), user_id (string)
```

### Chat Service
```
POST /api/chat/message
Body: { "user_id": "123", "message": "Hello!" }
```

### Quiz Service
```
POST /api/quiz/generate
Body: { "document_id": "doc123", "user_id": "123" }
```

### STT Service
```
POST /api/stt/transcribe
Form: file (audio), user_id (string)
```

### TTS Service
```
POST /api/tts/synthesize
Body: { "text": "Hello world", "user_id": "123" }
```

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## 🔄 CI/CD Pipeline

The project uses AWS CodeBuild for automated builds. The `buildspec.yml` defines:

1. **Install Phase**: Set up Python environment
2. **Pre-Build Phase**: Login to ECR, run unit tests
3. **Build Phase**: Build Docker images for all services
4. **Post-Build Phase**: Push images to ECR

## 📁 Project Structure

```
phase3_full_system/
├── api-gateway/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
├── chat-service/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
├── doc-service/
│   ├── Dockerfile
│   ├── document_service.py
│   ├── requirements.txt
│   └── utils.py
├── quiz-service/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
├── stt-service/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
├── tts-service/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
├── tests/
│   └── test.py
├── buildspec.yml
├── docker-compose.yml
├── create_dbs.py
└── README.md
```

## 🔐 AWS Services Used

- **Amazon RDS** - PostgreSQL database
- **Amazon S3** - Document and audio storage
- **AWS Secrets Manager** - Secure credential storage
- **Amazon ECR** - Docker container registry
- **AWS CodeBuild** - CI/CD builds
- **AWS CodePipeline** - Deployment automation

## 👤 Author

**Joeee14**

## 📄 License

This project is for educational purposes as part of a Cloud Computing course.

