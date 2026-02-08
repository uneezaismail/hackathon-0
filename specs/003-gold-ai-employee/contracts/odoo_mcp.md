# MCP Server Contract: Odoo Community Integration

**Server Name**: `odoo-mcp`
**File**: `My_AI_Employee/mcp_servers/odoo_mcp.py`
**Purpose**: Integrate with self-hosted Odoo Community (Odoo 19+) for accounting operations
**Authentication**: API Key or Username/Password (stored in OS credential manager)
**Base URL**: `http://localhost:8069` (configurable via .env)

---

## Overview

This MCP server provides tools for interacting with a self-hosted Odoo Community installation via JSON-RPC APIs. All financial operations (create_invoice, send_invoice, record_payment, create_expense) require HITL approval before execution.

---

## Tools

### 1. create_invoice

Create draft invoice in Odoo accounting system.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "customer_name": "string (required) - Customer name",
  "customer_email": "string (required) - Customer email for sending invoice",
  "invoice_date": "string (required) - Invoice date (YYYY-MM-DD)",
  "due_date": "string (required) - Payment due date (YYYY-MM-DD)",
  "line_items": [
    {
      "description": "string (required) - Line item description",
      "quantity": "number (required) - Quantity (>= 0)",
      "unit_price": "number (required) - Price per unit (>= 0)"
    }
  ],
  "tax_rate": "number (optional) - Tax rate (0-1, default: 0.0)",
  "notes": "string (optional) - Invoice notes"
}
```

#### Output Schema

```json
{
  "invoice_id": "string - Odoo invoice ID (e.g., INV/2026/0001)",
  "status": "string - draft",
  "total_amount": "number - Total amount including tax",
  "odoo_url": "string - URL to view invoice in Odoo",
  "created_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `ODOO_CONNECTION_ERROR`: Cannot connect to Odoo instance
- `CUSTOMER_NOT_FOUND`: Customer does not exist in Odoo
- `INVALID_DATE`: Invoice date or due date is invalid
- `VALIDATION_ERROR`: Line items validation failed

---

### 2. send_invoice

Validate and send invoice to customer via email.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "invoice_id": "string (required) - Odoo invoice ID",
  "email_subject": "string (optional) - Custom email subject",
  "email_body": "string (optional) - Custom email body"
}
```

#### Output Schema

```json
{
  "invoice_id": "string - Odoo invoice ID",
  "status": "string - sent",
  "email_sent": "boolean - true if email sent successfully",
  "sent_to": "string - Customer email address",
  "sent_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `INVOICE_NOT_FOUND`: Invoice ID does not exist
- `INVOICE_ALREADY_SENT`: Invoice already sent
- `EMAIL_SEND_FAILED`: Failed to send email
- `INVALID_STATUS`: Invoice not in correct status for sending

---

### 3. record_payment

Record payment against invoice and reconcile.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "invoice_id": "string (required) - Odoo invoice ID",
  "amount": "number (required) - Payment amount (> 0)",
  "payment_date": "string (required) - Payment date (YYYY-MM-DD)",
  "payment_method": "string (required) - bank_transfer | credit_card | cash | check",
  "reference": "string (optional) - Payment reference/memo"
}
```

#### Output Schema

```json
{
  "payment_id": "string - Odoo payment ID (e.g., PAY/2026/0001)",
  "invoice_id": "string - Related invoice ID",
  "status": "string - posted",
  "reconciled": "boolean - true if payment reconciled with invoice",
  "invoice_status": "string - paid | partial",
  "created_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `INVOICE_NOT_FOUND`: Invoice ID does not exist
- `INVALID_AMOUNT`: Payment amount invalid or exceeds invoice total
- `PAYMENT_DATE_INVALID`: Payment date is in the future
- `RECONCILIATION_FAILED`: Failed to reconcile payment with invoice

---

### 4. create_expense

Create expense record with optional receipt attachment.

**Requires HITL Approval**: NO (auto-approved for amounts < $100, otherwise requires approval)

#### Input Schema

```json
{
  "description": "string (required) - Expense description",
  "amount": "number (required) - Expense amount (> 0)",
  "expense_date": "string (required) - Date of expense (YYYY-MM-DD)",
  "category": "string (required) - Expense category (office_supplies, travel, meals, etc.)",
  "vendor": "string (optional) - Vendor name",
  "receipt_path": "string (optional) - Path to receipt file"
}
```

#### Output Schema

```json
{
  "expense_id": "string - Odoo expense ID (e.g., EXP/2026/0001)",
  "status": "string - draft | submitted",
  "category": "string - Expense category",
  "receipt_attached": "boolean - true if receipt attached",
  "created_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `INVALID_CATEGORY`: Expense category not found in Odoo
- `INVALID_AMOUNT`: Expense amount invalid
- `RECEIPT_NOT_FOUND`: Receipt file not found at specified path
- `EXPENSE_DATE_INVALID`: Expense date is in the future

---

### 5. generate_report

Generate financial report from Odoo accounting data.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "report_type": "string (required) - profit_loss | balance_sheet | cash_flow | aged_receivables",
  "start_date": "string (required) - Report start date (YYYY-MM-DD)",
  "end_date": "string (required) - Report end date (YYYY-MM-DD)",
  "format": "string (optional) - json | pdf (default: json)"
}
```

#### Output Schema

```json
{
  "report_type": "string - Report type",
  "period": {
    "start_date": "string - Start date",
    "end_date": "string - End date"
  },
  "data": {
    "revenue": "number - Total revenue",
    "expenses": "number - Total expenses",
    "net_income": "number - Net income (revenue - expenses)",
    "details": "object - Detailed breakdown by account"
  },
  "generated_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `INVALID_REPORT_TYPE`: Report type not supported
- `INVALID_DATE_RANGE`: Start date after end date
- `NO_DATA`: No accounting data for specified period

---

## Authentication

### API Key Method (Recommended)

```python
import odoorpc

odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('database_name', 'username', 'api_key')
```

### Username/Password Method

```python
import odoorpc

odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('database_name', 'username', 'password')
```

**Credential Storage**: Use OS credential manager (keyring library) to store credentials securely.

---

## Rate Limits

- **No rate limits** for self-hosted Odoo instance
- **Connection pooling**: Reuse connection for multiple operations
- **Timeout**: 30 seconds per operation

---

## Error Handling

### Retry Logic

- **Transient errors** (network timeout, connection refused): Retry with exponential backoff (1s, 2s, 4s, 8s)
- **Authentication errors**: Do NOT retry, alert user
- **Validation errors**: Do NOT retry, return error to user

### Graceful Degradation

- **Odoo unavailable**: Queue operations locally in `.odoo_queue.jsonl`
- **Process queue**: When Odoo becomes available, process queued operations
- **Alert user**: Notify when Odoo is unavailable

---

## Audit Logging

All operations MUST be logged to `/Logs/YYYY-MM-DD.json` with:
- Timestamp
- Action type (create_invoice, send_invoice, record_payment, create_expense, generate_report)
- Actor (system | user | autonomous_task)
- Target (customer name, invoice ID, expense ID)
- Approval status
- Result (success | failed | queued)
- Odoo record ID
- Financial amount (for financial operations)

**Credential Sanitization**: API keys and passwords MUST be sanitized before logging.

---

## Testing

### Unit Tests

```python
import pytest
from mcp.client import ClientSession, StdioServerParameters

@pytest.fixture
async def odoo_mcp_client():
    server_params = StdioServerParameters(
        command="python",
        args=["My_AI_Employee/mcp_servers/odoo_mcp.py"],
        env={"DRY_RUN": "true"}
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session

@pytest.mark.asyncio
async def test_create_invoice(odoo_mcp_client):
    result = await odoo_mcp_client.call_tool(
        "create_invoice",
        arguments={
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "invoice_date": "2026-01-27",
            "due_date": "2026-02-27",
            "line_items": [
                {"description": "Consulting", "quantity": 1, "unit_price": 1500.00}
            ]
        }
    )
    assert "invoice_id" in result.content[0].text
```

### Integration Tests

- Test with local Odoo instance (Docker container)
- Verify invoice creation, sending, payment recording
- Test error handling and retry logic

---

## Dependencies

```
odoorpc>=0.9.0
fastmcp>=0.1.0
pydantic>=2.0.0
keyring>=24.0.0
```

---

## Configuration (.env)

```bash
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo_db
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key_here
ODOO_MCP_PORT=3007
```
