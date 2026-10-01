# Store Interface API

A full-stack online store application built to practice backend system design, REST API development, relational database modeling, and transaction-based inventory management.

The system manages products, inventory, shopping carts, and orders while maintaining accurate stock levels through validated checkout logic.

## Features

### Inventory Management

* Create, update, and manage store inventory
* Track item stock levels
* Prevent purchases when inventory is insufficient
* Maintain accurate inventory after completed transactions

### Shopping Cart System

* Create and manage user carts
* Add, remove, and update cart items
* Validate requested quantities against available inventory
* Currently supports one active cart per user to maintain a simple structured workflow

### Order Processing

* Converts cart items into permanent order records
* Stores order history independently from active carts
* Captures item price at purchase time
* Removes purchased items from carts after checkout
* Maintains historical order data even if users are soft deleted

### Error Handling

The API provides structured error responses for:

* Missing users, carts, or items
* Invalid requests
* Insufficient inventory
* Database failures

Database rollbacks are used to prevent partial updates during failed transactions.

---

# System Design

The application follows a standard client-server architecture:

```
React UI
    |
    v
FastAPI REST API
    |
    v
PostgreSQL Database
```
### Backend Responsibilities

FastAPI handles:

* Request validation
* Business logic
* Cart and order processing
* Inventory validation
* Database communication

SQLAlchemy manages ORM models while Pydantic handles API schemas and validation.

---

# Database Design

The database uses a relational model with:

## Users

Stores user accounts and status.

* User ID
* Password hash
* Creation date
* Account status

Users are soft deleted to preserve historical order data.

## Items

Stores inventory information.

* Item ID
* Name
* Description
* Stock quantity
* Price

## Carts

Stores active shopping carts.

## Cart Items

Join table connecting carts and inventory items.

Uses a composite key:

```
(cart_id, item_id)
```

Tracks requested quantities.

## Orders

Stores completed purchases.

Includes:

* User reference
* Order total
* Order timestamp

## Order Items

Stores the purchased items at checkout.

Includes:

* Item reference
* Quantity purchased
* Price at time of order

This preserves historical order accuracy even if item prices change later.

---

# Tech Stack

## Frontend

* React
* Vite
* React Router
* Fetch API
* JavaScript

## Backend

* Python
* FastAPI
* SQLAlchemy ORM
* Pydantic
* Uvicorn

## Database

* PostgreSQL
* SQL

## Tools

* Docker
* Docker Compose
* Alembic (database migrations)

---

# Project Structure

```
store-interface/

backend/
├── app/
│   ├── routers/        # API routes
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic models
│   └── database.py     # Database connection
├── Dockerfile

frontend/
├── client/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── Dockerfile

docker-compose.yml
```

---

# Running the Project

## Using Docker

Start all services:

```bash
docker compose up --build
```

Services:
Frontend:
```
http://localhost:5173
```

API:
```
http://localhost:8000
```

Swagger Documentation:
```
http://localhost:8000/docs
```

---

# Database Migrations

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

Create migrations:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

---

# API Overview

## Items

```
GET    /items/get_all
POST   /items/add_item
GET    /items/{item_id}/details
PUT    /items/{item_id}/update
DELETE /items/{item_id}
```

## Cart

```
POST   /cart/{user_id}/newcart
GET    /cart/{user_id}/viewcart
POST   /cart/{user_id}/addItem
DELETE /cart/{user_id}/removeItem
```

## Orders

```
POST /orders/{user_id}/createorder
GET  /orders/{user_id}/vieworderdetails
GET  /orders/getallorders
```

---

# Design Decisions

### Inventory Safety

Before checkout:

1. Validate cart quantities
2. Compare requested amount with available stock
3. Complete order only if inventory is sufficient
4. Update inventory after successful purchase

This prevents overselling inventory.

### Order History

Orders are stored separately from carts.

Cart data represents current user activity.

Order data represents permanent transaction history.

---

## Authentication
The API uses signed JWT bearer tokens for protected routes. Configure `JWT_SECRET_KEY` in the repository-root `.env` file; it must contain at least 32 bytes. The API resolves this `.env` location from its own source path, so configuration works whether the server is started from the repository root or the `api/` directory. When using Docker Compose, the key is passed into the API container from the same `.env` file.

Tokens use the `HS256` algorithm and expire after 30 minutes by default. To override the lifetime, set `ACCESS_TOKEN_EXPIRE_MINUTES` to a value from 1 to 1440.

Log in with `POST /users/login` and the account email and password. The response includes an `access_token` and `token_type: "bearer"`. Send the token with protected API requests in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

The frontend stores the token after login and attaches it to API requests. Logging out removes the stored token. Tokens for inactive or suspended accounts are rejected.


# Future Improvements

## Security
* Role-based access
* Rate limiting
* Improved request validation
* add Permission controls

## Database
* Additional order history tables
* Transaction logging
* Query optimization
* Indexing improvements

## Cart Improvements
* Cart expiration
* Multiple carts per user
* Persistent abandoned carts

Environment example (keep the real `.env` file local and untracked):
```dotenv
DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
JWT_SECRET_KEY=
FRONTEND_PORT=
FRONTEND_URL=
```

Generate a unique signing key with `python -c "import secrets; print(secrets.token_urlsafe(48))"` and set it as `JWT_SECRET_KEY` in `.env`. Do not reuse the database password or commit the generated key.

## Database and Administrator Setup
Start PostgreSQL and the API with `docker compose up -d --build`. Apply schema migrations with `docker compose exec fastapi alembic upgrade head`, then create or promote an administrator using `docker compose exec fastapi python /app/api/create_admin.py admin@example.com`. The command prompts for a password only when creating a new account. Existing named database volumes keep their initialized PostgreSQL credentials; changing `POSTGRES_USER` or `POSTGRES_PASSWORD` in `.env` does not change credentials inside an existing volume.