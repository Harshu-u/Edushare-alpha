# EduShare (notes sharing)

This repo was scaffolded by adapting the CampusConnect (MyCollegeProject) code into a notes-sharing app.

Quick start (development):

1. Create & activate virtualenv

```bash
python -m venv .venv
source .venv/Scripts/activate  # on Windows bash
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment

- Copy `.env.example` to `.env` and fill values.
- To use PostgreSQL, set DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT in `.env`. If these are not set the project will use `sqlite3`.

4. Create PostgreSQL database (example using psql):

```sql
CREATE DATABASE edushare_db;
CREATE USER edushare_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE edushare_db TO edushare_user;
```

5. Run migrations and create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. Run dev server with HTTPS (devcert.pem/devkey.pem exist)

```bash
python manage.py runserver_plus 127.0.0.1:8000 --cert-file devcert.pem --key-file devkey.pem
```

Notes about pushing to GitHub

- You must authenticate to push. Use a Personal Access Token or `gh auth login`.
- Example push:

```bash
git remote add origin https://github.com/Harshu-u/Edushare-alpha.git
git branch -M main
git push -u origin main
```

If you encounter authentication errors, generate a PAT (repo scope) and use it as the password when prompted.

What I changed

- Added `core/forms.py` (custom registration form from CampusConnect adapted)
- Copied `register` and `login` templates (styled with Tailwind as in CampusConnect)
- Added drag-and-drop file upload UI for notes and a simple rating form
- Made `edushare/settings.py` support PostgreSQL via environment variables
- Added `psycopg2-binary` to `requirements.txt`

Next steps I can take (optional):

- Wire advanced rating UI (star icons and AJAX)
- Add tags, color-coded labels and dashboard statistics
- Copy additional CampusConnect static assets and pages (dashboard, profile)
- Help push the repo to GitHub (you will need to authenticate)
