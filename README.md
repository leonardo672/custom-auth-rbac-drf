# Custom Authentication & Authorization System (RBAC)

## Overview

This project implements a **custom authentication and authorization system** without relying on built-in framework authentication mechanisms.
The system provides:

* User registration and authentication
* Token-based session management
* Soft user deletion
* Role-based access control (RBAC)
* Admin-managed access rules
* Protected resource endpoints
* Proper HTTP status handling (401 / 403)

---

# Architecture

The system consists of three main components:

1. Authentication System
2. Role-Based Access Control (RBAC)
3. Protected Business Resources (Mock Views)

---

# Database Schema

## User Table

Stores user account information.

Fields:

* id (PK)
* first_name
* last_name
* middle_name
* email (unique)
* password_hash
* role (USER / ADMIN)
* is_active (soft delete flag)
* created_at
* updated_at

### Roles

Two roles are supported:

* USER — default role for registered users
* ADMIN — full access to manage users and permissions

---

## AuthToken Table

Stores active login sessions.

Fields:

* token (UUID)
* user (FK → User)
* created_at

This table is used to identify users in subsequent requests.

---

# Authentication Flow

## Registration

Endpoint:

POST /api/register/

Required fields:

* first_name
* last_name
* middle_name
* email
* password
* confirm_password

Behavior:

* Passwords must match
* Password is hashed
* Default role = USER
* User created with is_active = True

---

## Login

Endpoint:

POST /api/login/

Input:

* email
* password

Behavior:

* Validate credentials
* Check is_active
* Generate UUID token
* Store token in AuthToken table
* Return token

Response:

```
{
  "token": "uuid-token"
}
```

---

## Authentication for Requests

All protected endpoints require header:

Authorization: Bearer <token>

System behavior:

* Extract token
* Find user from AuthToken table
* Attach user to request
* If token missing → 401
* If invalid token → 401
* If user inactive → 403

---

## Logout

Endpoint:

POST /api/logout/

Behavior:

* Remove token from database
* User becomes unauthorized

---

## Soft Delete User

Endpoint:

DELETE /api/delete/

Behavior:

* Set is_active = False
* Delete token
* User cannot login again
* Account remains in database

---

## Update Profile

Endpoint:

PUT /api/profile/

User can update:

* first_name
* last_name
* middle_name

---

# Role-Based Access Control (RBAC)

Access control is implemented using **roles**.

Roles stored in:

User.role

Supported roles:

* USER
* ADMIN

---

# Admin Permissions

Only ADMIN users can:

* Get all users
* Create users
* Change user roles
* Access admin-only resources

---

# Admin Endpoints

## Get Current User

GET /api/me/

Returns authenticated user info.

---

## Get Users (Admin Only)

GET /api/users/

Responses:

401 → not authenticated
403 → not admin
200 → list of users

---

## Admin Create User

POST /api/admin/create-user/

Required fields:

* first_name
* last_name
* middle_name
* email
* password
* confirm_password
* role (USER or ADMIN)

Behavior:

* Admin only
* Password validation
* Password hashing
* Role assignment

---

## Change User Role

PATCH /api/admin/change-role/{user_id}/

Body:

```
{
  "role": "ADMIN"
}
```

Behavior:

* Admin only
* Updates user role

---

# Authorization Rules

| Condition             | Response         |
| --------------------- | ---------------- |
| No token              | 401 Unauthorized |
| Invalid token         | 401 Unauthorized |
| User inactive         | 403 Forbidden    |
| User lacks permission | 403 Forbidden    |
| Authorized access     | 200 OK           |

---

# Mock Business Resources

The system supports protected business resources.

Example:

GET /api/projects/
GET /api/reports/

Behavior:

* Not logged in → 401
* Logged in USER → limited access
* ADMIN → full access

These endpoints demonstrate RBAC functionality.

---

# Security Features

* Custom token authentication
* Password hashing
* Soft delete users
* Role-based permissions
* Admin-only endpoints
* Token invalidation on logout
* Token-based request identification

---

# Access Control Design Summary

Authentication → identifies user
Authorization → checks role
RBAC → controls access
Admin API → modifies permissions

Flow:

Login → receive token
Token → identify user
User role → check permission
Permission OK → return resource
Permission denied → 403

---

# Default Test Roles

Admin user:

role = ADMIN

Regular user:

role = USER

---

# HTTP Status Codes

| Code | Meaning                      |
| ---- | ---------------------------- |
| 200  | Success                      |
| 201  | Created                      |
| 400  | Validation error             |
| 401  | Unauthorized (not logged in) |
| 403  | Forbidden (no permission)    |
| 404  | Not found                    |

---

# Conclusion

This project implements a fully custom:

* Authentication system
* Token session management
* Role-based authorization
* Admin-controlled permissions
* Protected resource access

The system does not rely on built-in framework authentication and demonstrates a complete RBAC architecture.
