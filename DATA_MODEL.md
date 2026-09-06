# DistribuWatch — Data Model

## 1. Overview

DistribuWatch uses a relational database to store users, monitors, monitoring cycles, check results, incidents, and notification configuration.

The database is the persistent source of truth for the application.

The initial data model is intentionally simple and focused on the V1 monitoring workflow.

---

## 2. Entity Relationship Overview

```text
User
 |
 +---- Monitor
          |
          +---- Check Cycle
          |       |
          |       +---- Check Result
          |
          +---- Incident
          |
          +---- Notification Configuration
```

A user can create multiple monitors.

Each monitor is checked repeatedly through monitoring cycles.

Each monitoring cycle produces check results from multiple monitoring workers.

Incidents are created when the health state of a monitor changes significantly.

---

## 3. User

Represents a DistribuWatch user.

### Main fields

| Field | Description |
|---|---|
| id | Unique user identifier |
| email | User's email address |
| password | Hashed password |
| created_at | Account creation time |
| updated_at | Last update time |

A user can own multiple monitors.

---

## 4. Monitor

Represents a service or endpoint that DistribuWatch should monitor.

### Main fields

| Field | Description |
|---|---|
| id | Unique monitor identifier |
| user_id | Owner of the monitor |
| name | Human-readable monitor name |
| url | HTTP/HTTPS endpoint to check |
| interval_seconds | Monitoring interval |
| is_active | Whether monitoring is enabled |
| current_status | Current health state |
| created_at | Monitor creation time |
| updated_at | Last update time |

### Example

```text
Name: Production API
URL: https://api.example.com/health
Interval: 60 seconds
Status: UP
Active: Yes
```

---

## 5. Check Cycle

Represents one monitoring round for a monitor.

A cycle groups the observations from different monitoring workers so that they can be evaluated together.

### Main fields

| Field | Description |
|---|---|
| id | Unique cycle identifier |
| monitor_id | Monitor being checked |
| started_at | Time the cycle started |
| completed_at | Time the cycle completed |
| status | Cycle processing status |

### Example

```text
Monitor: Production API

Cycle: 1024

India  -> UP
Europe -> UP
US     -> DOWN
```

The cycle provides a common reference for comparing results from different observers.

---

## 6. Check Result

Represents the result produced by one monitoring worker during a check cycle.

### Main fields

| Field | Description |
|---|---|
| id | Unique result identifier |
| monitor_id | Monitor being checked |
| check_cycle_id | Monitoring cycle |
| worker_id | Monitoring worker identifier |
| region | Worker/observer region |
| status | Result status |
| http_status | HTTP response status |
| latency_ms | Response time |
| error_message | Error information when applicable |
| checked_at | Time of the check |

### Example

```text
Cycle: 1024

Worker: india-1
Region: India
Status: UP
HTTP: 200
Latency: 120ms
```

Another worker may produce:

```text
Worker: europe-1
Region: Europe
Status: DOWN
HTTP: 503
Latency: 850ms
```

Multiple results belonging to the same cycle are used by the health evaluation logic.

---

## 7. Incident

Represents a significant availability problem detected for a monitor.

An incident starts when the monitor enters a failure state according to the health evaluation rules and ends when the service recovers.

### Main fields

| Field | Description |
|---|---|
| id | Unique incident identifier |
| monitor_id | Affected monitor |
| status | Incident state |
| started_at | Incident start time |
| resolved_at | Incident resolution time |
| created_at | Record creation time |
| updated_at | Last update time |

### Example

```text
Monitor: Production API

Status: DOWN
Started: 10:30 AM
Resolved: 10:42 AM
```

An incident therefore represents a period of service unavailability or significant degradation.

---

## 8. Notification Configuration

Represents how a user wants to receive monitoring alerts.

### Main fields

| Field | Description |
|---|---|
| id | Unique configuration identifier |
| user_id | Owner of the configuration |
| monitor_id | Optional monitor association |
| channel | Notification type |
| destination | Email address, webhook URL, etc. |
| is_active | Whether notifications are enabled |
| created_at | Configuration creation time |
| updated_at | Last update time |

### Initial notification channels

V1 can support:

- Email
- Generic Webhook

More channels can be added later.

---

## 9. Relationships

### User → Monitor

One user can have many monitors.

```text
User 1
  |
  +---- Monitor 1
  |
  +---- Monitor 2
  |
  +---- Monitor 3
```

### Monitor → Check Cycle

One monitor can have many check cycles.

```text
Monitor
  |
  +---- Cycle 1
  |
  +---- Cycle 2
  |
  +---- Cycle 3
```

### Check Cycle → Check Result

One check cycle can have multiple check results because multiple monitoring workers participate in the same cycle.

```text
Cycle 100

 +---- India Worker
 |
 +---- Europe Worker
 |
 +---- US Worker
```

### Monitor → Incident

One monitor can have multiple incidents over its lifetime.

```text
Monitor
  |
  +---- Incident 1
  |
  +---- Incident 2
  |
  +---- Incident 3
```

### User / Monitor → Notification Configuration

Notification configuration can belong to a user and optionally be associated with a specific monitor.

This allows future support for both:

- User-wide notifications
- Monitor-specific notifications

---

## 10. Health States

The monitor's current status can use:

```text
UP
DEGRADED
DOWN
RECOVERED
```

The exact rules for changing between these states are part of the health evaluation logic rather than the database model itself.

---

## 11. Result Status

A check result represents what an individual worker observed.

For example:

```text
UP
DOWN
TIMEOUT
ERROR
UNKOWN - for new created monitor until it configured
```

The exact result categories can be refined during implementation.

The important distinction is:

> Check result = what one observer saw.

> Monitor health = what DistribuWatch determines after evaluating multiple observations.

---

## 12. Worker Identity

Each monitoring worker needs a stable identifier.

Example:

```text
india-1
europe-1
us-1
```

The worker identity allows DistribuWatch to understand where an observation came from and compare results from different monitoring locations.

Worker health should remain separate from monitor health.

---

## 13. Data Ownership

The database has clear ownership boundaries:

```text
User
    -> Account information

Monitor
    -> Monitoring configuration

Check Cycle
    -> Monitoring round

Check Result
    -> Individual observer result

Incident
    -> Service availability event

Notification Configuration
    -> Alert delivery settings
```

This separation keeps each model responsible for one major concept.

---

## 14. V1 Data Model Boundary

The initial database should focus only on the core monitoring workflow.

V1 includes:

- Users
- Monitors
- Check cycles
- Check results
- Incidents
- Notification configuration

The following are intentionally not required in the initial model:

- Billing
- Organizations
- Teams
- Complex RBAC
- Deployment records
- Dependency graphs
- AI/anomaly models
- Kubernetes resources
- Multiple monitoring protocols

These can be introduced later if real product requirements justify them.

---

## 15. Core Data Flow

The data model supports the following flow:

```text
User
 |
 v
Monitor
 |
 v
Check Cycle
 |
 +--------+--------+
 |        |        |
 v        v        v
Result  Result   Result
India   Europe     US
 |        |        |
 +--------+--------+
          |
          v
   Health Evaluation
          |
          v
       Monitor
        Status
          |
          v
       Incident
          |
          v
    Notification
```

---

## 16. Design Principle

The main data-model principle is:

> Store individual observations separately from the final service-health state.

This allows DistribuWatch to preserve what each monitoring worker observed while independently determining the overall health of the monitored service.

That separation is important for:

- Quorum-based health evaluation
- Regional comparison
- Incident detection
- Historical analysis
- Debugging monitoring disagreements
