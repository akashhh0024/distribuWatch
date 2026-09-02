# DistribuWatch — API

## 1. Overview

The DistribuWatch API is a REST API built with Django REST Framework.

It provides the interface between the frontend and the monitoring system.

The API is responsible for:

- User authentication
- Monitor management
- Viewing monitor health
- Viewing monitoring results
- Viewing incidents
- Managing notification configuration
- Application health checks

The V1 API focuses only on the functionality required by the initial monitoring platform.

---

## 2. Base URL

The API is exposed under:

```text
/api/
```

Example:

```text
GET /api/monitors/
```

Authentication-protected endpoints require a valid access token.

---

## 3. Authentication

DistribuWatch uses token-based authentication.

### Register

```text
POST /api/auth/register/
```

Creates a new user account.

### Request

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

### Login

```text
POST /api/auth/login/
```

### Request

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

### Response

```json
{
  "access": "access-token",
  "refresh": "refresh-token"
}
```

The access token is used for authenticated API requests.

Example:

```text
Authorization: Bearer <access-token>
```

### Refresh Token

```text
POST /api/auth/refresh/
```

Used to obtain a new access token.

---

## 4. Monitor API

Monitors are the main resources managed by users.

### Create Monitor

```text
POST /api/monitors/
```

Creates a new monitor.

### Request

```json
{
  "name": "Production API",
  "url": "https://api.example.com/health",
  "interval_seconds": 60
}
```

### Response

```json
{
  "id": 1,
  "name": "Production API",
  "url": "https://api.example.com/health",
  "interval_seconds": 60,
  "is_active": true,
  "current_status": "UP"
}
```

---

### List Monitors

```text
GET /api/monitors/
```

Returns the monitors belonging to the authenticated user.

Example response:

```json
[
  {
    "id": 1,
    "name": "Production API",
    "url": "https://api.example.com/health",
    "interval_seconds": 60,
    "is_active": true,
    "current_status": "UP"
  }
]
```

---

### Get Monitor

```text
GET /api/monitors/{id}/
```

Returns details about a specific monitor.

---

### Update Monitor

```text
PATCH /api/monitors/{id}/
```

Updates one or more monitor settings.

Example:

```json
{
  "interval_seconds": 120,
  "is_active": true
}
```

---

### Delete Monitor

```text
DELETE /api/monitors/{id}/
```

Deletes a monitor.

---

## 5. Monitor Status

The monitor's current health is available through the monitor resource.

Example:

```json
{
  "id": 1,
  "name": "Production API",
  "current_status": "DEGRADED"
}
```

Possible V1 states:

```text
UP
DEGRADED
DOWN
RECOVERED
```

The status is determined by the monitoring and health-evaluation system rather than directly by the frontend.

---

## 6. Check Results API

Check results represent individual observations made by monitoring workers.

### List Results

```text
GET /api/monitors/{id}/results/
```

Returns monitoring results for a monitor.

Example:

```json
[
  {
    "id": 101,
    "check_cycle_id": 50,
    "worker_id": "india-1",
    "region": "India",
    "status": "UP",
    "http_status": 200,
    "latency_ms": 120,
    "checked_at": "2026-09-02T12:00:00Z"
  },
  {
    "id": 102,
    "check_cycle_id": 50,
    "worker_id": "europe-1",
    "region": "Europe",
    "status": "DOWN",
    "http_status": 503,
    "latency_ms": 850,
    "checked_at": "2026-09-02T12:00:02Z"
  }
]
```

The frontend can use these results to display:

- Response time
- Worker/region status
- HTTP status
- Historical monitoring information

---

## 7. Check Cycles API

A check cycle represents one monitoring round.

### List Check Cycles

```text
GET /api/monitors/{id}/cycles/
```

Returns monitoring cycles associated with the monitor.

Example:

```json
[
  {
    "id": 50,
    "monitor_id": 1,
    "started_at": "2026-09-02T12:00:00Z",
    "completed_at": "2026-09-02T12:00:03Z",
    "status": "COMPLETED"
  }
]
```

Check cycles are primarily useful for grouping and analyzing observations from multiple workers.

---

## 8. Incident API

Incidents represent significant availability problems.

### List Incidents

```text
GET /api/monitors/{id}/incidents/
```

Returns incidents for a monitor.

Example:

```json
[
  {
    "id": 10,
    "monitor_id": 1,
    "status": "OPEN",
    "started_at": "2026-09-02T12:10:00Z",
    "resolved_at": null
  }
]
```

### Get Incident

```text
GET /api/incidents/{id}/
```

Returns details about a specific incident.

Incidents are created and resolved by the monitoring system. They are not manually created by the frontend in V1.

---

## 9. Notification API

Notification configuration determines where monitoring alerts should be delivered.

### List Notification Configurations

```text
GET /api/notifications/
```

Returns notification configurations belonging to the authenticated user.

### Create Notification Configuration

```text
POST /api/notifications/
```

Example:

```json
{
  "channel": "email",
  "destination": "user@example.com",
  "monitor_id": 1,
  "is_active": true
}
```

### Update Notification Configuration

```text
PATCH /api/notifications/{id}/
```

### Delete Notification Configuration

```text
DELETE /api/notifications/{id}/
```

Initial notification channels:

```text
email
webhook
```

Additional channels can be added later.

---

## 10. Health Endpoint

The backend provides a simple health endpoint.

```text
GET /api/health/
```

Example response:

```json
{
  "status": "ok"
}
```

This endpoint is useful for:

- Deployment checks
- Container health checks
- Load balancers
- Basic operational monitoring

---

## 11. Public Status API

The public status page may expose a read-only endpoint.

```text
GET /api/public/status/
```

This endpoint does not require authentication.

Example response:

```json
{
  "services": [
    {
      "name": "Production API",
      "status": "UP"
    },
    {
      "name": "Website",
      "status": "DEGRADED"
    }
  ]
}
```

Only information intended for public display should be returned.

---

## 12. API Request Flow

A typical user flow looks like:

```text
React Dashboard
      |
      v
POST /api/monitors/
      |
      v
Django API
      |
      v
Create Monitor
      |
      v
Scheduler starts monitoring
      |
      v
Monitoring Workers
      |
      v
Check Results
      |
      v
Health Evaluation
      |
      v
Monitor Status / Incident
      |
      v
React Dashboard
```

The frontend does not directly communicate with monitoring workers.

---

## 13. Authentication Flow

```text
User
 |
 v
Login
 |
 v
POST /api/auth/login/
 |
 v
Access Token
 |
 v
React stores authentication state
 |
 v
Authenticated API Requests
```

For example:

```text
GET /api/monitors/
Authorization: Bearer <access-token>
```

---

## 14. Error Responses

The API should return consistent JSON error responses.

Example:

```json
{
  "detail": "Monitor not found."
}
```

Common HTTP status codes include:

| Status | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 204 | Resource deleted successfully |
| 400 | Invalid request |
| 401 | Authentication required or invalid |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation error |
| 500 | Internal server error |

The exact error structure can be refined during implementation.

---

## 15. Authorization

Users should only be able to access resources they own.

For example:

```text
User A
 |
 +---- Monitor A
```

User A can access Monitor A.

If User B attempts to access Monitor A, the API should not expose the monitor's private data.

This ownership rule applies to:

- Monitors
- Check results
- Check cycles
- Incidents
- Notification configurations

Public status information is an intentional exception.

---

## 16. API Design Principles

The API follows a few simple principles:

### Resource-oriented

Endpoints represent resources such as:

```text
monitors
results
cycles
incidents
notifications
```

### Stateless authentication

Each authenticated request carries the required access token.

### Separation of responsibilities

The API manages application resources, while background workers perform monitoring checks.

### Read-only monitoring data

Monitoring results and incidents are generated by the monitoring system. Users primarily read this information through the API.

### Simple V1

The API should expose only functionality required by the initial product.

---

## 17. V1 API Boundary

V1 includes:

- User registration
- User login
- Token refresh
- Monitor CRUD
- Monitor status
- Check results
- Check cycles
- Incidents
- Notification configuration
- Backend health check
- Public status information

The following are intentionally outside the V1 API:

- Billing
- Teams
- Organizations
- Advanced RBAC
- Deployment integrations
- Kubernetes management
- AI/anomaly APIs
- Additional monitoring protocols

These can be introduced later when the product requires them.

---

## 18. API Summary

```text
Authentication
    POST   /api/auth/register/
    POST   /api/auth/login/
    POST   /api/auth/refresh/

Monitors
    POST   /api/monitors/
    GET    /api/monitors/
    GET    /api/monitors/{id}/
    PATCH  /api/monitors/{id}/
    DELETE /api/monitors/{id}/

Monitoring Data
    GET    /api/monitors/{id}/results/
    GET    /api/monitors/{id}/cycles/

Incidents
    GET    /api/monitors/{id}/incidents/
    GET    /api/incidents/{id}/

Notifications
    GET    /api/notifications/
    POST   /api/notifications/
    PATCH  /api/notifications/{id}/
    DELETE /api/notifications/{id}/

System
    GET    /api/health/

Public
    GET    /api/public/status/
```

---

## 19. API Goal

The API provides a clean boundary between the user-facing application and the monitoring system.

The main flow is:

```text
Frontend
   |
   v
REST API
   |
   +---- Application Data
   |
   +---- Monitoring Data
   |
   +---- Incident Data
   |
   +---- Notification Configuration
```

The API should remain simple enough for the frontend to consume easily while keeping monitoring and background-processing responsibilities inside the backend system.
