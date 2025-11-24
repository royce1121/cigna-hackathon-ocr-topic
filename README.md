# PhilHealth AI Assistant – Local Setup Guide

A Django web application for **PhilHealth ID lookup** and **PDF extraction/processing** using OCR and AI.

---

## 1. Clone the Repository

```bash
git clone https://github.com/royce1121/cigna-hackathon-ocr-topic.git
cd cigna-hackathon-ocr-topic
```

---

## 2. Create and Activate a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```


## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure the Database

### Default: SQLite

No extra configuration needed. Django will create `db.sqlite3` automatically.

---

## 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 6. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts for username, email, and password.

---

## 7. Load Fixtures (Sample Data)

If there are initial fixture files in `core/fixtures/`, load them:

```bash
python manage.py loaddata healthcare_form_assistant/fixtures/<fixture_file>.json
```

Example:

```bash
python manage.py loaddata healthcare_form_assistant/fixtures/member_demo.json
```

> This pre-populates your database with sample members or other data needed for testing.

---

## 8. Run the Development Server

```bash
python manage.py runserver
```

Visit in your browser:

```
http://127.0.0.1:8000/healthcare_ai/member/
```

---
