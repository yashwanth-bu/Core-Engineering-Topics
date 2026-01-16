# **Pymongo FastAPI App**

A **FastAPI application with MongoDB** demonstrating CRUD operations, structured responses, JWT authentication, and role-based access control.

This project evolves from a simple **Level 0 CRUD app** to a **Level 5 production-ready app**.

---

## **Table of Contents**

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [API Endpoints](#api-endpoints)
5. [Project Evolution](#project-evolution)
6. [Requirements](#requirements)

---

## **Features**

### Level 0 – Beginner CRUD

* Full CRUD operations for users
* Pydantic models for request and response
* Basic APIRouter usage
* MongoDB integration with PyMongo
* Structured JSON response with `ResponseModel`
* HTTP status codes

### Level 1 → Level 4 – Improvements

* Optional fields and default values
* Partial updates for users
* Serialization of ObjectIds
* Filtering, pagination, and sorting for GET `/users`
* Proper response consistency

### Level 5 – Production-ready

* **JWT authentication** (`/login`)
* **Password hashing** using bcrypt
* **Role-based access control (RBAC)**

  * Admin can create/update/delete any user
  * Regular users can update only their own profile via `/users/me`
* ObjectId safety and serialization
* Proper HTTP status codes and validation

---

## **Installation**

1. Clone the repository:

```bash
git clone <repo-url>
cd pymongo_fastapi_app
```

2. Create a virtual environment and activate:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the server:

```bash
uvicorn main:app --reload
```

Server will run on `http://127.0.0.1:8000/`

---

## **Usage**

* **Login to get JWT token**

```
POST /login
Form:
- username
- password
```

* **Admin actions**

  * Create user: `POST /users/create`
  * Update any user: `PUT /users/{user_id}`
  * Delete any user: `DELETE /users/{user_id}`

* **User actions**

  * Update own profile: `PUT /users/me`
  * View all users: `GET /users`
  * View user by ID: `GET /users/{user_id}`

---

## **API Endpoints**

| Method | Endpoint        | Role   | Description                             |
| ------ | --------------- | ------ | --------------------------------------- |
| POST   | `/login`        | Public | Login and get JWT token                 |
| GET    | `/users`        | Public | Get all users (with filters/pagination) |
| GET    | `/users/{id}`   | Public | Get user by ID                          |
| POST   | `/users/create` | Admin  | Create a new user                       |
| PUT    | `/users/{id}`   | Admin  | Update any user                         |
| PUT    | `/users/me`     | User   | Update own profile                      |
| DELETE | `/users/{id}`   | Admin  | Delete a user                           |

---

## **Project Evolution (Level 0 → Level 5)**

| Level | Features                                                                                    |
| ----- | ------------------------------------------------------------------------------------------- |
| 0     | Basic CRUD, Pydantic models, MongoDB integration, APIRouter, structured responses           |
| 1     | Optional fields, default values, better response structure                                  |
| 2     | Partial updates for users (`UserUpdateModel`)                                               |
| 3     | Serialization of ObjectIds, consistent JSON responses                                       |
| 4     | Filters, pagination, sorting for GET `/users`                                               |
| 5     | JWT authentication, password hashing, role-based access control (admin/user), secure routes |

---

## **Requirements**

See `requirements.txt`:

```
fastapi==0.111.1
uvicorn==0.25.0
pymongo[srv]==4.5.0
python-jose==3.3.0
passlib[bcrypt]==1.7.5
pydantic==2.7.1
```

---
