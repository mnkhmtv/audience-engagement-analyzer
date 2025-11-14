# Backend README

This directory contains the FastAPI‐based backend for EasyTravel. It provides REST endpoints for user management, authentication, semantic POI search, and personalized recommendations.

---

## 📁 Repository Structure

```
Backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── POIRouter.py        # /api/poi
│   │       ├── TokenRout.py        # /api/token
│   │       └── UserRout.py         # /api/user
│   ├── infrastructure/
│   │   ├── core/
│   │   │   └── config.py           # Settings loader
│   │   ├── db/
│   │   │   ├── session.py          # AsyncSession factory
│   │   │   └── init_db.py          # create_all on startup
│   │   └── repositories/
│   │       ├── UserRepository.py
│   │       └── (other repos…)      
│   ├── models/
│   │   ├── dbModels/
│   │   │   └── UserEntity.py       # SQLAlchemy user table
│   │   ├── dtoModels/
│   │   │   ├── UserDTO.py          # UserCreateDTO, UserOutDTO
│   │   │   ├── TokenDTO.py
│   │   │   ├── RefreshTokenDTO.py
│   │   │   └── POIOutDTO.py
│   │   └── InterestsEnum.py        # Allowed user interests
│   ├── services/
│   │   ├── AuthorizationService.py # AuthService: login, refresh, password hashing
│   │   ├── UserService.py          # Business logic for registering users
│   │   └── POIService.py           # Semantic search & recommendations
│   ├── main.py                     # FastAPI app, middleware, startup events
│   └── requirements.txt
└── Dockerfile                      # Build instructions for backend image
```

---

## 🖥️ Prerequisites

* **Python 3.11+**
* **PostgreSQL** database
* **Docker & Docker Compose** (optional, but recommended)

1. **FAISS index file**  
   We keep the heavy `poi_ivfpq.poi_ivfpq` on Google Drive rather than in Git.  
    download all files
    https://drive.google.com/drive/folders/1QCts-pkFMKhGErPVhY9i7WJI4ihmvG3f?usp=sharing
2. Copy to DIR like:
   - LaBSE_emb.npy -> /DLS/experiments/indexes/LaBSE_emb.npy
   - MiniLM-6-L12_emb.npy ->/DLS/experiments/indexes/MiniLM-6-L12_emb.npy
   - MiniLM-12-L6_emb.npy -> /DLS/experiments/indexes/MiniLM-12-L6_emb.npy
   - poi_embeddings.npy -> /DLS/Embeddings/poi_embeddings.npy
---

## ⚙️ Configuration

Environment variables (can be set in `.env` or via your deployment):

Copy .envexample and save it as .env

---

## 🚀 Running Locally

1. **Install dependencies**

   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL** (if not already running) and create the database.

3. **Run the app**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

On startup, `init_db` will automatically create all tables and optionally seed an owner user.

---

## 🐋 Running with Docker Compose

```bash
docker-compose up --build
```

* **Backend** will be accessible on `http://localhost:8000`.
* **PostgreSQL** on `localhost:5432`.

---

## 🔐 Authentication Flow

1. **Register**

   ```http
   POST /api/user/register
   Content-Type: application/json

   {
     "first_name":"Alice",
     "last_name":"Smith",
     "email":"alice@example.com",
     "password":"hunter2",
     "city":"Moscow",
     "interests":["museums","parks"],
     "about_me":"I love history",
     "additional_interests":"local cuisine"
   }
   ```

   → returns `UserOutDTO` (without password).

2. **Get Token**

   ```http
   POST /api/token/get-token
   Content-Type: application/x-www-form-urlencoded

   grant_type=password&username=alice@example.com&password=hunter2
   ```

   → returns `TokenDTO` with `access_token`, `refresh_token`.

3. **Refresh Token**

   ```http
   POST /api/token/refresh
   Content-Type: application/json

   { "refresh_token": "<refresh_token>" }
   ```

All subsequent calls require `Authorization: Bearer <access_token>` header.

---

## 📦 API Endpoints

### 1. User

| Method | Path                                             | Body            | Response     |
|--------|--------------------------------------------------|-----------------|--------------|
| `POST` | `/api/user/register`                             | `UserCreateDTO` | `UserOutDTO` |
| `PUT`  | `/api/user/update_interests`                     | `List[str]`     |              |
| `PUT`  | `/api/user/update_sity`                          | `str`           |              |
| `PUT`  | `/api/user/update_additional_interests`          | `str`           |              |
| `PUT`  | `/api/user/update_about_me`                      | `str`           |              |
| `GET`  | `/api/user/interests`                            | `int`           | `List[str]`  |

### 2. Authentication

| Method | Path                      | Body / Form                          | Response     |
|--------|---------------------------|--------------------------------------|--------------|
| `POST` | `/api/token/get-token`    | OAuth2PasswordRequestForm (email+pw) | `TokenDTO`   |
| `POST` | `/api/token/refresh`      | `RefreshTokenDTO`                    | `TokenDTO`   |
| `GET`  | `/api/token/current-user` | (Bearer token)                       | `UserOutDTO` |

### 3. POI Search & Recommendations

| Method | Path                                       | Query Params                                   | Response          |
| ------ | ------------------------------------------ | ---------------------------------------------- | ----------------- |
| `GET`  | `/api/poi/?q=<text>&city=<city>&limit=<n>` | `q` (required), `city` (opt), `limit` (1–50)   | `List[POIOutDTO]` |
| `GET`  | `/api/poi/recommendations?limit=<n>`       | `limit` (1–50), (uses user’s interests & city) | `List[POIOutDTO]` |

### 4. Favorites

| Method   | Path                                  | Response          |
|----------|---------------------------------------|-------------------|
| `POST`   | `/api/user/favorites/{poi_id}`        | `POIOutDTO`       |
| `GET`    | `/api/user/favorites`                 | `List[POIOutDTO]` |
---

## 📄 DTO Models

### `UserCreateDTO`

```python
first_name: str
last_name: str
email: EmailStr
password: str
city: str
interests: List[InterestsEnum]
about_me: str
additional_interests: str
```

### `UserOutDTO`

```python
id: UUID
first_name: str
last_name: str
email: EmailStr
city: str
interests: List[InterestsEnum]
about_me: str
additional_interests: str
```

### `TokenDTO`

```python
access_token: str
refresh_token: str
token_type: str  # "bearer"
```

### `RefreshTokenDTO`

```python
refresh_token: str
```

### `POIOutDTO`

```python
id: str
name: str
type: str
city: str
lat: float
lon: float
score: float      # FAISS similarity score
description: str  # enriched description
```

---

## ⚙️ Services Overview

* **AuthService** (`app/services/AuthorizationService.py`)

  * `login_for_access_token`, `refresh_access_token`
  * Password hashing, JWT token generation & verification

* **UserService** (`app/services/UserService.py`)

  * `add_user(dto, session)`

* **POIService** (`app/services/POIService.py`)

  * `search_in_city(query, city, top_n, expand_k, tags)`
  * `recommend_by_interests(interests, additional_interests, city, top_n)`

---

## 📝 Notes

* **Dependency Injection** via FastAPI’s `Depends` for DB sessions, services, and current user.
* **Database Schema** is created via SQLAlchemy’s `metadata.create_all` on startup.
* **Configuration** is centralized in `app/infrastructure/core/config.py`.

For detailed API docs, visit `http://localhost:8000/docs` once the server is running.
