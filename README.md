# anti-addiction-app

An application supporting addiction recovery, powered by GPT for personalized interactions and motivational support.

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/TropDog/anti-addiction-app.git
   cd anti-addiction-app/backend
   ```

2. Create and activate a virtual environment (Windows PowerShell):
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. Start the FastAPI server locally:
    ```bash
    uvicorn app.main:app --reload
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