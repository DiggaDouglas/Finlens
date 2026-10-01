# FinLens

## Local setup

1. Create and activate a virtual environment:

	```powershell
	py -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```

2. Install dependencies:

	```powershell
	python -m pip install -r requirements.txt
	```

3. Create a `.env` file in the project root. Keep it local; `.env*` files are ignored by Git. Set the database values and the credentials for the initial accounts:

	```dotenv
	ENVIRONMENT=development
	APP_TIMEOUT_SECONDS=10
	MONGO_URI=mongodb://localhost:27017
	MONGO_DB_NAME=finlens_db
	MODEL_CHECKPOINT=nlpaueb/legal-bert-base-uncased
	MAX_TOKEN_LENGTH=256
	SEED_ADMIN_EMAIL=admin@example.com
	SEED_ADMIN_PASSWORD=replace-with-a-unique-strong-password
	SEED_REGULATOR_EMAIL=regulator@example.com
	SEED_REGULATOR_PASSWORD=replace-with-a-different-unique-strong-password
	```

	Use unique passwords and do not commit the `.env` file or share its contents.

## Seed the database

Start MongoDB, configure the `.env` values above, then run:

```powershell
python seed_db.py
```

The script creates the initial SuperAdmin and Regulator accounts only when their email addresses are not already present. It hashes the supplied passwords and does not clear existing users or audit logs. Both initial accounts are marked to change their password after signing in.
