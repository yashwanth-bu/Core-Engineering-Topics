# Pymongo Async FastAPI App

A **production-ready FastAPI project** using **Motor (async MongoDB driver)**, featuring **JWT authentication**, **role-based access control**, **password hashing**, **full CRUD**, and **advanced querying** (filtering, pagination, sorting).

---

## Features

* **Async CRUD operations** with MongoDB
* **JWT Authentication** with `/login` endpoint
* **Password hashing** using `bcrypt`
* **Role-Based Access Control (RBAC)**:

  * Admin can create, update, delete any user
  * Regular users can only update/view their own profile
* **GET /users** supports:

  * Filtering by username
  * Min/Max age filter
  * Pagination (`skip` and `limit`)
  * Sorting (`sort_by` and `sort_order`)
* Proper **HTTP status codes** and **structured responses**
* **ObjectId serialization** (converted to string)
* **Production-ready async code**

---

## Requirements

* Python 3.11+
* MongoDB running locally or remotely

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the App

```bash
uvicorn main:app --reload
```

* `main` → your Python file name
* `--reload` → auto-reloads on code changes

App will run at: `http://127.0.0.1:8000`

---

## Database Setup

* Default MongoDB URL: `mongodb://localhost:27017`
* Database name: `mydatabase`
* Collection: `users`

> Passwords are stored hashed using **bcrypt**.

---

## Authentication

* **Register / Create User** → Admin-only via `/users/create`
* **Login** → `/login` with form data (`username`, `password`)
* Returns **JWT token** (Bearer token)

Include token in requests for protected routes:

```
Authorization: Bearer <access_token>
```

---

## User Endpoints

### Create User (Admin Only)

```
POST /users/create
```

**Body**:

```json
{
  "username": "alice",
  "password": "securepassword",
  "userage": 25,
  "role": "user"
}
```

---

### Login

```
POST /login
```

**Form Data**:

* `username`
* `password`

**Response**:

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

---

### Get All Users (Admin Only)

```
GET /users/
```

**Query Parameters (Optional)**:

* `username` → filter by username substring
* `min_age` → minimum age
* `max_age` → maximum age
* `skip` → pagination start
* `limit` → pagination limit
* `sort_by` → field name (default: username)
* `sort_order` → `asc` or `desc`

---

### Get Single User (Admin or Self)

```
GET /users/{user_id}
```

---

### Update User (Admin or Self)

```
PUT /users/{user_id}
```

**Body** (any field to update):

```json
{
  "username": "newname",
  "password": "newpassword",
  "userage": 30
}
```

---

### Delete User (Admin Only)

```
DELETE /users/{user_id}
```

---

## Response Format

All endpoints return a **structured response**:

```json
{
  "message": "User fetched successfully",
  "response_status": true,
  "response_data": { ... } // or list of users
}
```

---

## Security Notes

* Passwords are **never returned** in responses
* JWT tokens expire in **30 minutes** (configurable)
* Only **admins** can perform sensitive operations
* Regular users can **only view/update their own data**

---

## Project Structure

```
.
├── main.py             # FastAPI app (Level 5)
├── requirements.txt    # Dependencies
├── README.md           # Project documentation
```

> For production, consider splitting routers, models, and auth into separate modules.

---
