# PAS Server
Flask API for a password manager that handles users, sessions, and encrypted password records backed by Supabase.

## What it does
- Creates user accounts and issues JWT-based sessions
- Stores and retrieves password entries for authenticated users
- Supports update/delete/search workflows for saved passwords
- Logs login attempts to a dedicated table

## Key features
- Auth & sessions: create-user and login endpoints; JWTs include a 3-day expiry
- Password vault: create/get/update/delete password records scoped to a user
- Search: case-insensitive search across title, username, email, and URL fields
- Data protection: bcrypt hashing for user passwords; Fernet encryption for stored password values
- Supabase persistence: uses `users`, `passwords`, and `logins` tables via the Supabase Python SDK
- Consistent responses: JSON shape `{success, msg, data}` from `lib/response.py`

## Tech stack
- Python
- Flask + Flask-Cors
- Supabase Python SDK
- PyJWT
- bcrypt + cryptography (Fernet)
- python-dotenv
- Vercel serverless functions (via `vercel.json` rewrite)

## Architecture overview
The Flask app lives in `api/index.py`. Route handlers call helper modules in `lib/` for crypto, sessions, and response formatting, and `db/index.py` for Supabase queries.

```text
Client
  |
  v
Flask routes (api/index.py)
  |-- lib/session.py (JWT)
  |-- lib/encrypter.py (bcrypt/Fernet)
  |-- lib/response.py (response shape)
  v
db/index.py -> Supabase tables: users, passwords, logins
```

## Getting started (local)

### Prerequisites
- Python environment with pip
- Vercel CLI (for local dev via `vercel dev`)

### Install
```bash
pip install -r requirements.txt
```

### Environment variables
These are required and loaded via `python-dotenv` in `api/index.py`.

```bash
SUPABASE_URL=...
SUPABASE_KEY=...
SECRET=...
```

### Run
```bash
vercel dev
```

## Usage
Set a base URL for your environment:

```bash
BASE_URL=http://localhost:3000
```

Create a user:
```bash
curl -X POST "$BASE_URL/api/create-user" \
  -H "Content-Type: application/json" \
  -d '{"ip":"127.0.0.1","email":"user@example.com","username":"alice","password":"secret"}'
```

Log in:
```bash
curl -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{"ip":"127.0.0.1","username":"alice","password":"secret"}'
```

Use the returned session token in the `Authorization` header (the code reads the second space-delimited value):

```bash
TOKEN=...
curl -X POST "$BASE_URL/api/create-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: <type> $TOKEN" \
  -d '{"title":"GitHub","username":"alice","email":"user@example.com","password":"vault-secret","url":"https://github.com"}'
```

Fetch saved passwords:
```bash
curl -X GET "$BASE_URL/api/get-passwords" \
  -H "Authorization: <type> $TOKEN"
```

Search passwords:
```bash
curl -X GET "$BASE_URL/api/search-passwords?query=github%20alice" \
  -H "Authorization: <type> $TOKEN"
```

Update a password:
```bash
curl -X PUT "$BASE_URL/api/update-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: <type> $TOKEN" \
  -d '{"id":"<password-id>","title":"GitHub (work)"}'
```

Delete a password:
```bash
curl -X DELETE "$BASE_URL/api/delete-password?id=<password-id>" \
  -H "Authorization: <type> $TOKEN"
```

Verify a session:
```bash
curl -X GET "$BASE_URL/api/verify-session" \
  -H "Authorization: <type> $TOKEN"
```

## Testing / Quality
No automated tests, linting, or typecheck configs are present in this repository.

## Deployment
`vercel.json` rewrites all routes to `/api/index`, so the Flask app is deployed as a Vercel Serverless Function.
