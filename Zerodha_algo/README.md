# Zerodha_algo

Setup and quick run:

1. Create a Python venv and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file from the example and add secrets (do NOT commit):

```bash
cp .env.example .env
# edit .env to set API_KEY, API_SECRET
```

3. Generate an access token (one-time, short-lived):

```bash
python generate_token.py
```

4. Run the algo (paper mode by default):

```bash
python main.py
```

DRY RUN:
- To avoid placing live orders even if `MODE=LIVE`, set `DRY_RUN=true` in your `.env` file. This will simulate orders and record them to `logs/trades.csv`.

Notes:
- Use the `.venv` Python interpreter in your editor and CI.
- Do not commit `.env` or secrets to git.
