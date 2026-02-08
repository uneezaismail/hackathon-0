---
name: odoo-integration
description: >
  Integrate with Odoo Community (self-hosted ERP) for accounting, invoicing, and business management
  via JSON-RPC APIs (Odoo 19+). Handles invoice creation, payment tracking, expense categorization,
  and financial reporting. Use when: (1) Creating or sending invoices, (2) Recording payments or
  expenses, (3) Querying financial data, (4) Generating financial reports, (5) Managing accounting
  operations. Trigger phrases: "create invoice", "record payment", "track expenses", "odoo accounting",
  "financial report", "send invoice", "categorize expense".
---

# Odoo Integration

Integrate with Odoo Community (self-hosted ERP) for accounting, invoicing, and business management via JSON-RPC APIs.

## Overview

Gold tier requires creating an accounting system using **Odoo Community** (self-hosted, local) and integrating via MCP server using Odoo's JSON-RPC APIs (Odoo 19+). This skill manages all Odoo operations with approval workflow for financial actions.

**Key Capabilities:**
- Invoice creation and management
- Payment tracking and reconciliation
- Expense categorization
- Financial reporting
- Customer/vendor management

**Why Odoo Community?**
- Self-hosted, local-first (no cloud dependency)
- Free and open-source
- Comprehensive ERP features
- JSON-RPC API for integration
- Suitable for small business accounting

## Quick Start

### Setup Odoo Community

```bash
# Install Odoo Community 19+ (local)
# See references/odoo-installation.md for detailed setup

# Start Odoo server
./odoo-bin -c odoo.conf

# Access Odoo web interface
http://localhost:8069
```

### Create Invoice

```bash
/odoo-integration "Create invoice for Client A: $1,500 for January consulting"
```

### Record Payment

```bash
/odoo-integration "Record payment received: $1,500 from Client A for Invoice #INV/2026/001"
```

### Generate Financial Report

```bash
/odoo-integration "Generate monthly financial report for January 2026"
```

## Configuration

### In Company_Handbook.md

```markdown
## Odoo Accounting Rules

### Auto-Approve Thresholds
- Invoices: Auto-create draft invoices (require approval before sending)
- Payments < $50: Auto-record if from known customer
- Expenses < $100: Auto-categorize based on vendor

### Always Require Approval
- Invoices before sending to customer
- Payments > $50
- New customer/vendor creation
- Expense categorization changes
- Financial report generation

### Accounting Policies
- Invoice terms: Net 30
- Late payment fee: 1.5% per month
- Expense categories: Office, Travel, Software, Marketing, Professional Services
- Tax rate: 10% (adjust per jurisdiction)
```

### In .env

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=my_business
ODOO_USERNAME=admin
ODOO_PASSWORD=your_secure_password
ODOO_MCP_PORT=3007

# Odoo API Version
ODOO_API_VERSION=19.0
```

## Odoo MCP Server

### Capabilities

**Invoicing:**
- Create draft invoices
- Send invoices to customers
- Track invoice status (draft, sent, paid, overdue)
- Generate invoice PDFs

**Payments:**
- Record customer payments
- Record vendor payments
- Reconcile payments with invoices
- Track payment methods

**Expenses:**
- Create expense records
- Categorize expenses
- Attach receipts
- Track expense status

**Reporting:**
- Profit & Loss statement
- Balance sheet
- Cash flow report
- Aged receivables/payables

### MCP Actions

```python
# Invoice operations
create_invoice(customer_id, line_items, due_date)
send_invoice(invoice_id)
get_invoice_status(invoice_id)
generate_invoice_pdf(invoice_id)

# Payment operations
record_payment(invoice_id, amount, payment_method, date)
reconcile_payment(payment_id, invoice_id)
get_payment_status(payment_id)

# Expense operations
create_expense(amount, category, vendor, description, date)
attach_receipt(expense_id, file_path)
categorize_expense(expense_id, category)

# Reporting operations
generate_profit_loss(start_date, end_date)
generate_balance_sheet(date)
generate_cash_flow(start_date, end_date)
get_aged_receivables()
```

## Workflow

### 1. Invoice Creation

When client requests invoice:

```markdown
# /Needs_Action/20260127_143000_invoice_client_a.md

---
type: action_item
source: whatsapp
received: 2026-01-27T14:30:00Z
---

# Invoice Request

Client A requested invoice for January consulting work.

**Amount**: $1,500
**Services**: Consulting - January 2026
**Due date**: Net 30
```

Claude processes:

```markdown
# /Plans/Plan_invoice_client_a.md

## Objective
Create and send invoice to Client A

## Steps
- [x] Query Odoo for Client A customer record
- [x] Create draft invoice with line items
- [ ] Generate invoice PDF
- [ ] Send invoice via email (requires approval)

## Approval Required
Invoice must be approved before sending to customer.
```

Creates approval request:

```markdown
# /Pending_Approval/APPROVAL_20260127_invoice_client_a.md

---
type: approval_request
action: send_invoice
invoice_id: INV/2026/001
amount: 1500.00
customer: Client A
status: pending
---

## Invoice Details

**Invoice #**: INV/2026/001
**Customer**: Client A (client_a@example.com)
**Amount**: $1,500.00
**Due Date**: 2026-02-26 (Net 30)

**Line Items**:
- Consulting Services - January 2026: $1,500.00

## To Approve
Move this file to /Approved folder.
```

### 2. Payment Recording

When payment received:

```markdown
# /Needs_Action/20260128_100000_payment_client_a.md

---
type: action_item
source: email
received: 2026-01-28T10:00:00Z
---

# Payment Received

Bank notification: $1,500 received from Client A
Reference: INV/2026/001
```

Claude processes:

```
Query Odoo for invoice INV/2026/001
       ↓
Record payment via Odoo MCP
       ↓
Reconcile payment with invoice
       ↓
Update invoice status to "Paid"
       ↓
Log to audit trail
       ↓
Move to /Done/
```

### 3. Expense Categorization

When expense detected:

```markdown
# /Needs_Action/20260127_150000_expense_software.md

---
type: action_item
source: email
received: 2026-01-27T15:00:00Z
---

# Expense Receipt

Receipt from Software Vendor: $99/month subscription
```

Claude processes:

```
Extract expense details (amount, vendor, date)
       ↓
Categorize expense (Software)
       ↓
Create expense record in Odoo
       ↓
Attach receipt PDF
       ↓
Log to audit trail
       ↓
Move to /Done/
```

### 4. Financial Reporting

Weekly/monthly financial reports:

```bash
/odoo-integration "Generate monthly financial report for January 2026"
```

Claude queries Odoo:

```
Query Profit & Loss for January
Query Balance Sheet as of Jan 31
Query Cash Flow for January
Query Aged Receivables
       ↓
Aggregate data
       ↓
Generate report in /Briefings/
       ↓
Include in CEO briefing
```

## Usage Examples

### Example 1: Create Invoice

```bash
/odoo-integration "Create invoice for Client B: $2,500 for website development"
```

Result:
- Creates draft invoice in Odoo
- Generates invoice PDF
- Creates approval request in /Pending_Approval/
- After approval, sends invoice via email

### Example 2: Record Payment

```bash
/odoo-integration "Record payment: $1,500 from Client A for Invoice #INV/2026/001"
```

Result:
- Records payment in Odoo
- Reconciles with invoice
- Updates invoice status to "Paid"
- Logs to audit trail

### Example 3: Categorize Expense

```bash
/odoo-integration "Categorize expense: $150 to Office Supplies from Staples"
```

Result:
- Creates expense record in Odoo
- Categorizes as "Office Supplies"
- Logs to audit trail

### Example 4: Financial Report

```bash
/odoo-integration "Generate Q1 2026 financial summary"
```

Result:
- Queries Odoo for Q1 data
- Generates Profit & Loss, Balance Sheet, Cash Flow
- Creates report in /Briefings/
- Includes key metrics and trends

## Integration with Other Skills

### With ceo-briefing-generator

Financial data included in weekly CEO briefing:

```
ceo-briefing-generator queries odoo-integration
       ↓
Retrieves revenue, expenses, cash flow
       ↓
Includes in CEO briefing under "Financial Summary"
```

### With mcp-executor

Approved financial actions executed via Odoo MCP:

```
approval-workflow-manager approves invoice
       ↓
mcp-executor routes to Odoo MCP
       ↓
Odoo MCP sends invoice via email
       ↓
Logs execution to audit trail
```

### With ralph-wiggum-runner

Autonomous accounting operations:

```bash
/ralph-loop "Process all accounting tasks in /Needs_Action using @odoo-integration"
```

## Safety Features

- **Approval workflow**: All financial actions require approval
- **Audit logging**: All Odoo operations logged with timestamps
- **Dry-run mode**: Test operations without affecting Odoo data
- **Backup integration**: Automatic Odoo database backups
- **Reconciliation checks**: Verify payments match invoices

## Resources

- **references/odoo-installation.md** - Odoo Community setup guide
- **references/odoo-api.md** - Odoo JSON-RPC API documentation
- **references/accounting-workflows.md** - Common accounting workflows
- **scripts/odoo_client.py** - Odoo API client library
- **scripts/create_invoice.py** - Invoice creation script
- **scripts/record_payment.py** - Payment recording script
- **scripts/generate_report.py** - Financial report generator
