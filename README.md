# EduSphere

EduSphere is a Flask-based learning management system for students, institutes, and administrators. It supports user signup and login, institute course publishing, enrollments, quiz results, certificates, and an admin dashboard.

## Stack

- Python + Flask
- PostgreSQL via psycopg2
- Jinja templates with static CSS and JavaScript assets
- SMTP email for OTP and result notifications

## Environment Variables

Create a `.env` file in the project root with the values from `.env.example`.

- `FLASK_SECRET_KEY`: Flask session secret
- `FLASK_DEBUG`: set to `true` for local debug mode
- `SESSION_COOKIE_SECURE`: set to `true` in HTTPS deployments
- `SESSION_LIFETIME_HOURS`: session lifetime in hours
- `OTP_EXPIRY_MINUTES`: institute login OTP lifetime in minutes
- `ADMIN_EMAIL`: admin login email
- `ADMIN_PASSWORD`: admin login password
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL connection settings
- `SMTP_SENDER_EMAIL`, `SMTP_SENDER_PASSWORD`: SMTP credentials for OTP/result emails
- `SMTP_HOST`, `SMTP_PORT`: SMTP server settings
- `LOG_LEVEL`: optional application log level

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and fill in your secrets.
4. Make sure PostgreSQL is running and the expected tables already exist.
5. Start the app:

```bash
python app.py
```

## Notes

- Institute logins require SMTP credentials so the OTP email can be delivered.
- Admin credentials are no longer hardcoded in source; they must come from environment variables.
- Static asset references are Flask-relative, so the app is safer to deploy outside a Windows-only path layout.
