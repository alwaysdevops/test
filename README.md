# Event Registration

A simple Flask application for event registration with SQLite storage, HTML pages, JSON API endpoints, tests, Docker support, Jenkins pipeline configuration, and SonarQube project settings.

## Project Structure

```text
app.py
requirements.txt
Dockerfile
Jenkinsfile
sonar-project.properties
README.md
.gitignore
database/app.db
templates/
static/
tests/
screenshots/
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

## API

Create a registration:

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Asha Rao","email":"asha@example.com","event":"Cloud Workshop"}'
```

List registrations:

```bash
curl http://localhost:5000/api/users
```

## Test

```bash
pytest -q
```

The Selenium test is skipped automatically unless a browser driver is available.

## Docker

```bash
docker build -t event-registration .
docker run -p 5000:5000 event-registration
```
