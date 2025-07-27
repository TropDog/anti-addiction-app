# anti-addiction-app

An application supporting addiction recovery, powered by GPT for personalized interactions and motivational support.

---

## Setup

1. Create your own `.env` file with the following config variables:
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - POSTGRES_HOST
    - POSTGRES_PORT
    - ALGORITHM
    - JWT_SECRET_KEY
    - ACCESS_TOKEN_EXPIRE_MINUTES

2. Make sure you have Docker and Docker Compose installed.

## Usage

1. Run services from main directory:
    ```bash
    docker-compose up --build
    ```

2. Check the health endpoint:
    Open your browser and go to http://127.0.0.1:8000/health  
    You should see the JSON response:  
    ```json
    {"status":"ok"}
    ```
    
## Contribution

Contribution guidelines will be added soon.
For now, feel free to open issues and submit proposals.