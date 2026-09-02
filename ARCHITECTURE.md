# DistribuWatch — Architecture

## 1. Overview

DistribuWatch is a self-hosted monitoring platform for checking the availability of APIs and services from multiple independent monitoring locations.

The main problem it solves is:

> Is my service actually down, or can only some monitoring locations not reach it?

Instead of relying on a single monitoring server, DistribuWatch uses multiple monitoring workers. Their results are collected and evaluated to determine the health of the monitored service.

---

## 2. High-Level Architecture


                         User
                           |
                           v
                  React + TypeScript
                    Web Dashboard
                           |
                           v
                    Django + DRF
                     Backend API
                           |
              +------------+------------+
              |                         |
              v                         v
           MySQL                     Redis
      Source of Truth            Queue / Cache
                                        |
                                        v
                                     Celery
                                  Task System
                                        |
                         +--------------+--------------+
                         |              |              |
                         v              v              v
                      Worker A       Worker B       Worker C
                       India          Europe           US
                         |              |              |
                         +--------------+--------------+
                                        |
                                        v
                                  Check Results
                                        |
                                        v
                             Health / Incident
                                Evaluation
                                        |
                         +--------------+--------------+
                         |                             |
                         v                             v
                  Notification System          Status / Dashboard


---

## 3. Main Components

### Frontend

**React + TypeScript**

The frontend provides the user interface for:

- Creating monitors
- Viewing monitor health
- Viewing response times
- Viewing incidents
- Viewing historical results
- Managing monitoring configuration

The frontend communicates with the backend through REST APIs.

### Backend API

**Django + Django REST Framework**

The backend is responsible for:

- User authentication
- Monitor management
- Storing monitoring configuration
- Providing monitoring data to the frontend
- Managing incidents
- Determining service health
- Managing notifications

Django acts as the central application layer of DistribuWatch.

### Database

**MySQL**

MySQL stores persistent application data such as:

- Users
- Monitors
- Monitoring results
- Monitoring cycles
- Incidents
- Notification configuration

The database is the main source of truth for the application.

### Redis

**Redis** is used for fast, temporary operations such as:

- Celery task messaging
- Caching frequently accessed data
- Supporting background processing

Redis is not the primary source of persistent monitoring data.

### Scheduler

**Celery Beat**

Celery Beat periodically triggers monitoring cycles.

For example:


Monitor: Production API
Interval: 60 seconds


Every 60 seconds, a new monitoring cycle is started.

### Monitoring Workers

Monitoring workers perform the actual HTTP/HTTPS checks.

Example:


                 API
            /     |                /      |            Worker A  Worker B  Worker C
       India     Europe      US
         |         |          |
        UP        UP         DOWN


Each worker independently checks the target service and records the result.

A worker can record information such as:

- HTTP status
- Response time
- Success/failure
- Error information
- Check timestamp
- Worker/region

Multiple workers allow DistribuWatch to distinguish between:

- The service being globally unavailable
- A regional connectivity problem
- A problem affecting only one monitoring worker

---

## 4. Monitoring Flow

The basic monitoring flow is:


Celery Beat
    |
    v
Start Monitoring Cycle
    |
    v
Send checks to monitoring workers
    |
    +----------+----------+
    |          |          |
    v          v          v
 Worker A   Worker B   Worker C
    |          |          |
    +----------+----------+
               |
               v
         Store Results
               |
               v
        Evaluate Health
               |
        +------+------+
        |             |
        v             v
     Healthy        Problem
                       |
                       v
                    Incident
                       |
                       v
                  Notification


---

## 5. Check Cycles

A check cycle represents one monitoring round.

For example, if a monitor runs every 60 seconds:


Cycle 1
India  -> UP
Europe -> UP
US     -> UP

Cycle 2
India  -> UP
Europe -> DOWN
US     -> UP

Cycle 3
India  -> DOWN
Europe -> DOWN
US     -> DOWN


Results from the same cycle are evaluated together.

This allows the system to compare what different monitoring workers observed at approximately the same time.

---

## 6. Health Determination

DistribuWatch does not immediately declare a service DOWN because one worker failed.

Instead, results from multiple workers are evaluated together.

Example:


India  -> UP
Europe -> UP
US     -> DOWN


One worker failed while two succeeded.

The system should not immediately treat this as a confirmed global outage. It may indicate a degraded state or a possible regional/network issue.

If multiple independent workers report failure:


India  -> DOWN
Europe -> DOWN
US     -> DOWN


there is much stronger evidence that the monitored service is actually unavailable.

This is the basic idea behind DistribuWatch's **quorum-based health determination**.

---

## 7. Important Distinction

A monitoring worker failing is not automatically the same as the monitored service failing.

For example:


API
 |
 +---- India Worker  -> Worker itself is unavailable
 |
 +---- Europe Worker -> API is UP
 |
 +---- US Worker     -> API is UP


In this situation, the system should avoid incorrectly declaring the API DOWN.

Worker health and service health are therefore treated as separate concepts.

---

## 8. Health States

DistribuWatch uses a simple service health model:


UP
 |
 | failure detected
 v
DEGRADED
 |
 | majority/all observers fail
 v
DOWN
 |
 | service recovers
 v
RECOVERED
 |
 v
UP


The exact transition rules are handled by the health evaluation logic.

The purpose of these states is to give users a clearer picture than a simple UP/DOWN status.

---

## 9. Incident Flow

When the system detects a meaningful health-state change, it can create an incident.

Example:


Service is UP
      |
      v
Multiple workers detect failure
      |
      v
Health evaluation
      |
      v
Service becomes DOWN
      |
      v
Incident created
      |
      v
Notification sent
      |
      v
Service recovers
      |
      v
Incident resolved


An incident represents a period during which a monitored service experienced a significant availability problem.

---

## 10. Notification System

Notifications are handled separately from the main monitoring process.

This prevents notification delivery from blocking monitoring.

Example:


Health Evaluation
       |
       v
Incident Created
       |
       v
Notification Task
       |
       +---------> Email
       |
       +---------> Webhook


Additional notification channels can be added later without changing the core monitoring system.

---

## 11. Dashboard Flow

The dashboard retrieves monitoring information through the Django API.


React Dashboard
      |
      v
Django REST API
      |
      v
    MySQL
      |
      v
Monitor / Incident / Result Data
      |
      v
React Dashboard


Redis can be used to cache frequently requested information such as public status information.

---

## 12. Public Status Page

DistribuWatch can optionally provide a public status page.

Example:


DistribuWatch Status

API              Operational
Website          Operational
Payment Service  Degraded


The status page uses the same health information produced by the monitoring system.

---

## 13. Why Multiple Workers?

A single monitoring server can produce misleading results.

Example:


                    API
                     |
               +-----+-----+
               |           |
            India        Europe
           Observer     Observer
              |             |
             DOWN           UP


The API may not actually be globally down.

The problem could be:

- Regional network failure
- Internet routing issue
- DNS issue
- Monitoring worker problem
- Connectivity problem between the observer and service

Multiple independent workers provide more evidence before declaring a global outage.

---

## 14. Deployment Architecture

DistribuWatch is designed to be self-hosted.

A typical deployment can contain:


Docker Compose
     |
     +---- Django API
     |
     +---- React Frontend
     |
     +---- MySQL
     |
     +---- Redis
     |
     +---- Celery Beat
     |
     +---- Monitoring Workers
     |
     +---- Notification Worker


Monitoring workers can later be deployed in different geographic regions.

---

## 15. Data Flow Summary

The complete system can be understood as:


User
 |
 v
React Dashboard
 |
 v
Django API
 |
 v
Create Monitor
 |
 v
Scheduler
 |
 v
Monitoring Cycle
 |
 v
Multiple Monitoring Workers
 |
 v
HTTP/HTTPS Checks
 |
 v
Check Results
 |
 v
Health Evaluation
 |
 +-------> UP
 |
 +-------> DEGRADED
 |
 +-------> DOWN
 |
 +-------> RECOVERED
 |
 v
Incident Management
 |
 v
Notifications
 |
 v
Dashboard / Status Page


---

## 16. Architecture Principle

The core architectural principle of DistribuWatch is:

> Use multiple independent observations to make service-health decisions instead of trusting a single monitoring location.

The system is divided into clear responsibilities:


Frontend
    -> User interface

Django
    -> Application and API

MySQL
    -> Persistent data

Redis / Celery
    -> Background task processing

Monitoring Workers
    -> Perform service checks

Health Evaluation
    -> Determine service state

Incident Management
    -> Track outages

Notification System
    -> Inform users


Each component has a specific responsibility while working together as one monitoring platform.

---

## 17. V1 Architecture Boundary

The first version intentionally keeps the architecture simple.

V1 focuses on:

- HTTP/HTTPS monitoring
- Multiple monitoring workers
- Health determination
- Incident detection
- Basic notifications
- Dashboard
- Public status page
- Docker-based deployment

Technologies such as Kafka, Kubernetes, complex service meshes, and additional microservices are not required for the initial version.

They can be considered later if real requirements justify them.

---

## 18. Future Extensions

The architecture can later support:

- Additional monitoring regions
- DNS monitoring
- TCP monitoring
- SSL certificate monitoring
- Custom request headers
- POST/API checks
- Deployment correlation
- Dependency monitoring
- Advanced analytics
- Anomaly detection
- Intelligent alerting

These features should be added only when they solve a real user problem.

---

## 19. Architecture Goal

The goal of the architecture is not to make DistribuWatch unnecessarily complex.

The goal is to make the monitoring result more reliable by answering:

> Is my service actually unhealthy, or is the problem limited to one monitoring location?

The architecture achieves this by combining:

**central application management + scheduled background checks + independent monitoring workers + aggregated health evaluation + incident and notification systems.**
