# DistribuWatch

## 1. Product Overview

DistribuWatch is an open-source, self-hosted monitoring platform for
websites, APIs, and services.

It monitors the same target from multiple independent observer workers
and compares their results to determine whether a service is actually
unhealthy or whether the failure may be isolated to a particular
region/network.

The goal is to reduce false outage alerts and give engineers better
visibility into where an availability problem is occurring.

---

## 2. The Problem

When an API becomes unreachable, a monitoring system running from only
one location cannot easily answer:

- Is the API actually down?
- Is only this monitoring region unable to reach it?
- Is there a regional networking problem?
- Are different observers getting different results?
- Is this a temporary failure or a genuine outage?

For example:

India observer  → UP
Europe observer → UP
US observer     → DOWN

A single-region monitoring system may report the service as DOWN.

DistribuWatch can recognize that the observers disagree and avoid
immediately treating the service as globally unavailable.

If multiple independent observers report failure:

India observer     → DOWN
Europe observer    → DOWN
US observer        → DOWN
Singapore observer → DOWN

there is much stronger evidence that the target itself is unavailable.

---

## 3. Target Users

Primary users:

- Backend engineers
- Full-stack engineers
- DevOps / SRE engineers
- Small engineering teams
- Developers running their own APIs or websites

Especially useful for teams that:

- operate services across regions
- want self-hosted monitoring
- need visibility into regional failures
- want control over monitoring data
- want to avoid depending entirely on third-party monitoring services

---

## 4. Product Goal

The primary product question is:

> "Is my service actually down, or can only some monitoring regions
> not reach it?"

DistribuWatch should help answer that question quickly and reliably.

---

## 5. Core User Flow

A user should be able to:

1. Create an account or be provisioned by an administrator.
2. Create a monitor.
3. Provide the target URL.
4. Configure the monitoring interval.
5. Select/configure observer workers.
6. DistribuWatch periodically checks the target.
7. Multiple observers independently report their results.
8. DistribuWatch evaluates the observations.
9. The monitor receives a health state.
10. If a genuine failure is detected, an incident is created.
11. Configured notification channels receive an alert.
12. When the service recovers, the incident is resolved.
13. The user can inspect the incident and historical check results.

---

## 6. MVP

### Monitoring

V1 supports HTTP/HTTPS monitoring.

Each monitor contains:

- Name
- URL
- Check interval
- Active/inactive state
- Configured quorum
- Observer workers

Each check records:

- Worker/observer
- Check cycle
- Result
- HTTP status
- Response latency
- Error information
- Timestamp

---

## 7. Health States

A monitor can have the following states:

- UP
- DEGRADED
- DOWN
- RECOVERED

### UP

Observers are successfully reaching the target.

### DEGRADED

Observers disagree about the target's health.

Example:

2 observers → UP
1 observer → DOWN

This indicates a possible regional/network-specific problem rather
than enough evidence for a confirmed global outage.

### DOWN

The configured quorum of observers reports failure.

Example:

2 of 3 observers → DOWN

### RECOVERED

A previously unhealthy monitor has successfully recovered according
to the recovery rules.

The exact state transition rules will be defined in the architecture
and state-machine design.

---

## 8. Incidents

An incident represents a confirmed service availability problem.

An incident should contain:

- Monitor
- Start time
- Current state
- Resolution time
- Trigger information
- Relevant check-cycle information

A new incident is created when a monitor transitions into DOWN.

The incident is resolved when the monitor transitions back to UP.

---

## 9. Notifications

Notifications must be asynchronous.

Initial notification channels:

- Email
- Generic webhook

A notification should be generated when an incident is created or
resolved.

Duplicate processing must not result in duplicate alerts.

Notification delivery should be isolated from monitoring checks so
that a slow notification provider cannot block monitoring work.

The roadmap explicitly separates notification workers from check
workers and requires idempotent alert handling. :contentReference[oaicite:1]{index=1}

---

## 10. Dashboard

The dashboard should allow users to see:

### Overview

- Total monitors
- UP monitors
- DEGRADED monitors
- DOWN monitors
- Active incidents

### Monitor

- Current health
- URL
- Check interval
- Latest observer results
- Response latency
- Recent check history

### Incident

- Incident state
- Started at
- Resolved at
- Observer results
- Timeline of status changes

---

## 11. Public Status Page

Users should be able to expose a read-only public status page.

The status page should show:

- Services/monitors
- Current status
- Active incidents
- Recent incident history

It must not expose private monitor configuration or authentication
data.

The roadmap also specifies Redis caching for dashboard/status reads. :contentReference[oaicite:2]{index=2}

---

## 12. What DistribuWatch Will NOT Do in V1

To prevent scope creep, V1 will NOT include:

- Mobile applications
- Kubernetes monitoring
- Full infrastructure monitoring
- Log aggregation
- Distributed tracing
- Billing/subscriptions
- Dozens of notification integrations
- AI-based prediction
- Automatic root-cause analysis
- Complex cloud-provider integrations
- TCP/DNS/SSL monitoring

V1 focuses on one problem:

> Reliable HTTP/HTTPS availability monitoring from multiple observers.

---

## 13. Root Cause Limitation

DistribuWatch detects and compares availability observations.

It cannot automatically know the root cause of an outage.

For example, if an API goes DOWN, the system cannot inherently know
whether the cause was:

- a deployment
- database failure
- application crash
- infrastructure failure
- DNS issue
- network failure

Later versions may correlate monitoring incidents with deployment
or infrastructure events.

---

## 14. Success Criteria

DistribuWatch is successful if a user can:

1. Add a production API.
2. Have it checked automatically.
3. Receive observations from multiple independent workers.
4. See when observers disagree.
5. Distinguish a likely regional issue from a confirmed outage.
6. Receive an alert when an outage is confirmed.
7. See when the service recovers.
8. Inspect what happened during the incident.

The most important product metric is:

> Can the system detect unhealthy services quickly while reducing
> false outage alerts?

---

## 15. MVP Definition of Done

The MVP is complete when:

- A user can create a monitor.
- The monitor is checked automatically.
- Multiple independent workers can observe the same target.
- Each observation is stored with its worker identity.
- Results can be grouped into a check cycle.
- Worker disagreement is visible.
- A quorum determines confirmed DOWN status.
- Monitor status follows explicit transition rules.
- Incidents are automatically created and resolved.
- Notifications are sent asynchronously.
- Duplicate alerts are prevented.
- A dashboard shows monitor health.
- A public status page can expose service status.
- The complete system can be self-hosted with documented setup.

---

## 16. Product Principle

DistribuWatch should optimize for:

> Accurate information about service availability,
> not simply more alerts.

The system should prefer showing:

"Observers disagree — possible regional connectivity issue"

over immediately claiming:

"Production API is DOWN."

Only when sufficient independent evidence exists should the system
declare a confirmed outage.