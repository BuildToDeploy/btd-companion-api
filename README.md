
# BTD Companion API

  ![enter image description here](https://olive-chemical-haddock-701.mypinata.cloud/ipfs/bafkreibar6iqk742ixhn7ps5fd6c5t76wsymj7lpmfgixmn5gp5pp5r5ba)

**Community-driven, self-hosted backend for intelligent Ethereum smart contract analysis.** Deploy on your own infrastructure with full data control and multi-AI provider support.

  

BTD Companion is an open-source platform that empowers developers to analyze, optimize, and monitor Ethereum smart contracts using cutting-edge AI. Built for the community, by the community.

  

---

  

## ✨ Features

  

-  **AI-Powered Analysis** - Multi-provider AI support (OpenAI, Claude, Grok) with automatic fallback logic

-  **Contract Optimization** - Get intelligent suggestions to improve gas efficiency and security

-  **Real-Time Monitoring** - Track deployed contracts and monitor on-chain activity

-  **Self-Hosted** - Complete control over your data and infrastructure

-  **Community-Driven** - Open-source and ready for contributions

-  **Production-Ready** - FastAPI backend with PostgreSQL persistence, Docker deployment, and comprehensive error handling

  

---

  

## 🚀 Quick Start

  

### Prerequisites

  

- Docker & Docker Compose

- Python 3.11+ (for local development)

- PostgreSQL 14+ (included in docker-compose)

  

### Installation

  

1.  **Clone the repository**

```bash

git https://github.com/BuildToDeploy/btd-companion-api

cd btd-companion-api

```

  

2.  **Configure environment variables**

```bash

cp .env.example .env

```

Edit `.env` and add your API keys:

```env

# Database

DATABASE_URL=postgresql://btd_user:btd_password@postgres:5432/btd_companion

  

# AI Providers (add at least one)

OPENAI_API_KEY=your_openai_key

ANTHROPIC_API_KEY=your_claude_key

XAI_API_KEY=your_grok_key

  

# API Configuration

API_KEY=your_secure_api_key

DEBUG=False

```

  

3.  **Start the backend**

```bash

docker-compose up

```

  

The API will be available at `http://localhost:8000`

- API Docs: `http://localhost:8000/docs`

- ReDoc: `http://localhost:8000/redoc`

  

---

  

## 📖 API Endpoints

  

### Analyze Contract

```bash

POST  /api/analyze-contract

Content-Type:  application/json

Authorization:  Bearer  YOUR_API_KEY

  

{

"contract_address":  "0x...",

"contract_code":  "pragma solidity..."

}

```

  

### Optimize Contract

```bash

POST  /api/optimize-contract

Content-Type:  application/json

Authorization:  Bearer  YOUR_API_KEY

  

{

"contract_address":  "0x...",

"contract_code":  "pragma solidity..."

}

```

  

### Deploy Contract

```bash

POST  /api/deploy

Content-Type:  application/json

Authorization:  Bearer  YOUR_API_KEY

  

{

"contract_code":  "pragma solidity...",

"network":  "ethereum",

"constructor_args": []

}

```

  

### Monitor Contract

```bash

GET  /api/monitor/{contract_address}

Authorization:  Bearer  YOUR_API_KEY

```

  

### List Contracts

```bash

GET  /api/contracts

Authorization:  Bearer  YOUR_API_KEY

```

  

---

  

## 🛠️ Development

  

### Local Setup (without Docker)

  

1.  **Create virtual environment**

```bash

python -m venv venv

source venv/bin/activate # On Windows: venv\Scripts\activate

```

  

2.  **Install dependencies**

```bash

pip install -r requirements.txt

```

  

3.  **Run migrations**

```bash

alembic upgrade head

```

  

4.  **Start the server**

```bash

uvicorn app.main:app --reload

```

  

### Project Structure

````
btd-companion-api/
├── app/
│ ├── __init__.py
│ ├── main.py # FastAPI app entry point
│ ├── config.py # Configuration management
│ ├── database.py # Database setup and session
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic schemas
│ ├── security.py # Authentication & security
│ ├── ai_providers/
│ │ ├── base.py
│ │ ├── openai_provider.py
│ │ ├── claude_provider.py
│ │ └── grok_provider.py
│ └── routes/
│ ├── contracts.py
│ ├── analysis.py
│ ├── optimization.py
│ ├── deployment.py
│ └── monitoring.py
├── alembic/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md

````

  
  

---

  

## 🔐 Authentication

  

All API endpoints require an API key. Include it in your requests:

  

```bash

curl  -H  "Authorization: Bearer YOUR_API_KEY"  \

http://localhost:8000/api/contracts

```

  

Manage API keys in the database via the `/api/users` endpoints or by creating users directly.

  

---

  

## 🤖 AI Providers

  

BTD Companion supports multiple AI providers for redundancy and flexibility:

  

-  **OpenAI** - GPT-4 models (recommended for advanced analysis)

-  **Claude** - Anthropic's Claude models (excellent for code review)

-  **Grok** - xAI's Grok models (latest frontier model)

  

The system automatically falls back to the next provider if one fails. Configure at least one provider in `.env`.

  

---

  

## 📦 Deployment

  

### Docker Compose (Recommended)

```bash

docker-compose  up  -d

```

  

### Manual Docker Build

```bash

docker  build  -t  btd-companion-api  .

docker  run  -p  8000:8000  --env-file  .env  btd-companion-api

```

  

### Production Considerations

- Use environment variables for all secrets (never commit `.env`)

- Enable HTTPS/SSL with a reverse proxy (Nginx, Traefik)

- Use a managed PostgreSQL service (RDS, Supabase, Render)

- Set `DEBUG=False` in production

- Implement rate limiting for API endpoints

- Monitor logs and set up alerts

  

---

  

## 🧪 Testing

  

```bash

pytest

pytest  --cov=app  # With coverage

pytest  -v  # Verbose

```

  

---

  

## 🤝 Contributing

  

We welcome contributions from the community!

  

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)

5. Open a Pull Request

  

Please ensure:

- Code follows PEP 8 style guidelines

- All tests pass (`pytest`)

- New features include tests

- Documentation is updated

  

---

  

## 📝 License

  

This project is licensed under the MIT License - see the LICENSE file for details.

  

---

  

## 🤔 Support & Community

  

-  **Issues** - Report bugs or request features on GitHub Issues

-  **Discussions** - Join community discussions on GitHub Discussions

-  **Email** - support@btdcompanion.com

  

---

  

## 🌟 Star History

  

If you find BTD Companion useful, please consider giving us a star! It helps the project grow and reach more developers.

  

---

  

**Made with ❤️ by the BTD Companion Community**