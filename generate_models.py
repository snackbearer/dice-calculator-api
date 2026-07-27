from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

database_url = os.getenv("DATABASE_URL")

subprocess.run([
    "sqlacodegen",
    database_url,
    "--outfile",
    "app/models/generated_models.py"
], check=True)