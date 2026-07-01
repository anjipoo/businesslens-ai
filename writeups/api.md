# API Documentation

## POST /projects

Creates a new business project.

Request

```json
{
  "company_name": "Acme Corp",
  "industry": "Retail",
  "description": "Sales have declined over the last year."
}
```

Response

```json
{
  "id": 1,
  "status": "created"
}
```

---

## POST /projects/{id}/analyze

Starts the multi-agent analysis pipeline.

Response

```json
{
  "status": "running"
}
```

---

## GET /analyses/{id}

Returns the latest analysis.

Includes

- execution status
- agent logs
- final report

---

## Health Endpoint

Returns API availability.

```
GET /health
```

Response

```
{
    "status":"healthy"
}
```