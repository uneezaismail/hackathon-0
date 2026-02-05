#!/usr/bin/env python3
"""
Unit tests for Odoo MCP Server.

Tests all 5 tools:
1. create_invoice
2. send_invoice
3. record_payment
4. create_expense
5. generate_report

Uses DRY_RUN=true mode to avoid actual Odoo operations.
"""

import pytest
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set DRY_RUN mode for testing
os.environ['DRY_RUN'] = 'true'
os.environ['ODOO_URL'] = 'http://localhost:8069'
os.environ['ODOO_DATABASE'] = 'test_db'
os.environ['ODOO_USERNAME'] = 'test_user'
os.environ['ODOO_API_KEY'] = 'test_key'

try:
    from mcp.client import ClientSession, StdioServerParameters
    MCP_CLIENT_AVAILABLE = True
except ImportError:
    MCP_CLIENT_AVAILABLE = False
    pytest.skip("MCP client not available", allow_module_level=True)


@pytest.fixture
async def odoo_mcp_client():
    """Create MCP client session for Odoo server."""
    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent.parent / "My_AI_Employee" / "mcp_servers" / "odoo_mcp.py")],
        env={
            "DRY_RUN": "true",
            "ODOO_URL": "http://localhost:8069",
            "ODOO_DATABASE": "test_db",
            "ODOO_USERNAME": "test_user",
            "ODOO_API_KEY": "test_key"
        }
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session


# ============================================================================
# T011: Unit test for create_invoice tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_invoice_success(odoo_mcp_client):
    """Test successful invoice creation."""
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    result = await odoo_mcp_client.call_tool(
        "create_invoice",
        arguments={
            "customer_name": "Test Customer Inc",
            "customer_email": "billing@testcustomer.com",
            "invoice_date": today,
            "due_date": due_date,
            "line_items": [
                {
                    "description": "Consulting Services - January 2026",
                    "quantity": 40,
                    "unit_price": 150.00
                },
                {
                    "description": "Software Development",
                    "quantity": 1,
                    "unit_price": 5000.00
                }
            ],
            "tax_rate": 0.10,
            "notes": "Payment terms: Net 30"
        }
    )

    # Parse result
    response = json.loads(result.content[0].text)

    # Assertions
    assert "invoice_id" in response
    assert response["status"] == "draft"
    assert "total_amount" in response
    assert response["total_amount"] > 0
    assert "odoo_url" in response
    assert "created_at" in response


@pytest.mark.asyncio
async def test_create_invoice_validation_error(odoo_mcp_client):
    """Test invoice creation with invalid data."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "create_invoice",
            arguments={
                "customer_name": "Test Customer",
                "customer_email": "invalid-email",  # Invalid email
                "invoice_date": "2026-01-27",
                "due_date": "2026-02-27",
                "line_items": [
                    {"description": "Service", "quantity": -1, "unit_price": 100}  # Negative quantity
                ]
            }
        )
    assert "validation" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_invoice_empty_line_items(odoo_mcp_client):
    """Test invoice creation with empty line items."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "create_invoice",
            arguments={
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "invoice_date": "2026-01-27",
                "due_date": "2026-02-27",
                "line_items": []  # Empty line items
            }
        )
    assert "line_items" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()


# ============================================================================
# T012: Unit test for send_invoice tool
# ============================================================================

@pytest.mark.asyncio
async def test_send_invoice_success(odoo_mcp_client):
    """Test successful invoice sending."""
    result = await odoo_mcp_client.call_tool(
        "send_invoice",
        arguments={
            "invoice_id": "INV/2026/0001",
            "email_subject": "Invoice INV/2026/0001 from Your Company",
            "email_body": "Please find attached your invoice. Payment is due within 30 days."
        }
    )

    # Parse result
    response = json.loads(result.content[0].text)

    # Assertions
    assert response["invoice_id"] == "INV/2026/0001"
    assert response["status"] == "sent"
    assert response["email_sent"] is True
    assert "sent_to" in response
    assert "sent_at" in response


@pytest.mark.asyncio
async def test_send_invoice_not_found(odoo_mcp_client):
    """Test sending non-existent invoice."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "send_invoice",
            arguments={
                "invoice_id": "INV/9999/9999"  # Non-existent invoice
            }
        )
    assert "not found" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_send_invoice_default_message(odoo_mcp_client):
    """Test sending invoice with default email message."""
    result = await odoo_mcp_client.call_tool(
        "send_invoice",
        arguments={
            "invoice_id": "INV/2026/0002"
            # No custom email_subject or email_body
        }
    )

    response = json.loads(result.content[0].text)
    assert response["email_sent"] is True


# ============================================================================
# T013: Unit test for record_payment tool
# ============================================================================

@pytest.mark.asyncio
async def test_record_payment_success(odoo_mcp_client):
    """Test successful payment recording."""
    payment_date = datetime.now().strftime("%Y-%m-%d")

    result = await odoo_mcp_client.call_tool(
        "record_payment",
        arguments={
            "invoice_id": "INV/2026/0001",
            "amount": 6600.00,
            "payment_date": payment_date,
            "payment_method": "bank_transfer",
            "reference": "Wire transfer - Ref: WT20260127001"
        }
    )

    # Parse result
    response = json.loads(result.content[0].text)

    # Assertions
    assert "payment_id" in response
    assert response["invoice_id"] == "INV/2026/0001"
    assert response["status"] == "posted"
    assert "reconciled" in response
    assert "invoice_status" in response
    assert "created_at" in response


@pytest.mark.asyncio
async def test_record_payment_invalid_amount(odoo_mcp_client):
    """Test payment recording with invalid amount."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "record_payment",
            arguments={
                "invoice_id": "INV/2026/0001",
                "amount": -100.00,  # Negative amount
                "payment_date": "2026-01-27",
                "payment_method": "bank_transfer"
            }
        )
    assert "amount" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_record_payment_future_date(odoo_mcp_client):
    """Test payment recording with future date."""
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "record_payment",
            arguments={
                "invoice_id": "INV/2026/0001",
                "amount": 1000.00,
                "payment_date": future_date,  # Future date
                "payment_method": "cash"
            }
        )
    assert "date" in str(exc_info.value).lower() or "future" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_record_payment_partial(odoo_mcp_client):
    """Test partial payment recording."""
    result = await odoo_mcp_client.call_tool(
        "record_payment",
        arguments={
            "invoice_id": "INV/2026/0001",
            "amount": 3000.00,  # Partial payment
            "payment_date": datetime.now().strftime("%Y-%m-%d"),
            "payment_method": "credit_card",
            "reference": "Partial payment 1 of 2"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["invoice_status"] in ["partial", "paid"]


# ============================================================================
# T014: Unit test for create_expense tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_expense_success(odoo_mcp_client):
    """Test successful expense creation."""
    expense_date = datetime.now().strftime("%Y-%m-%d")

    result = await odoo_mcp_client.call_tool(
        "create_expense",
        arguments={
            "description": "Office supplies - printer paper and toner",
            "amount": 85.50,
            "expense_date": expense_date,
            "category": "office_supplies",
            "vendor": "Office Depot"
        }
    )

    # Parse result
    response = json.loads(result.content[0].text)

    # Assertions
    assert "expense_id" in response
    assert response["status"] in ["draft", "submitted"]
    assert response["category"] == "office_supplies"
    assert "created_at" in response


@pytest.mark.asyncio
async def test_create_expense_with_receipt(odoo_mcp_client):
    """Test expense creation with receipt attachment."""
    result = await odoo_mcp_client.call_tool(
        "create_expense",
        arguments={
            "description": "Business lunch with client",
            "amount": 125.00,
            "expense_date": datetime.now().strftime("%Y-%m-%d"),
            "category": "meals",
            "vendor": "Restaurant ABC",
            "receipt_path": "/path/to/receipt.pdf"
        }
    )

    response = json.loads(result.content[0].text)
    assert "expense_id" in response
    # In DRY_RUN mode, receipt attachment is simulated
    assert "receipt_attached" in response


@pytest.mark.asyncio
async def test_create_expense_invalid_category(odoo_mcp_client):
    """Test expense creation with invalid category."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "create_expense",
            arguments={
                "description": "Test expense",
                "amount": 50.00,
                "expense_date": "2026-01-27",
                "category": "invalid_category_xyz"  # Invalid category
            }
        )
    assert "category" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_expense_zero_amount(odoo_mcp_client):
    """Test expense creation with zero amount."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "create_expense",
            arguments={
                "description": "Test expense",
                "amount": 0.00,  # Zero amount
                "expense_date": "2026-01-27",
                "category": "office_supplies"
            }
        )
    assert "amount" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


# ============================================================================
# T015: Unit test for generate_report tool
# ============================================================================

@pytest.mark.asyncio
async def test_generate_report_profit_loss(odoo_mcp_client):
    """Test profit & loss report generation."""
    start_date = "2026-01-01"
    end_date = "2026-01-31"

    result = await odoo_mcp_client.call_tool(
        "generate_report",
        arguments={
            "report_type": "profit_loss",
            "start_date": start_date,
            "end_date": end_date,
            "format": "json"
        }
    )

    # Parse result
    response = json.loads(result.content[0].text)

    # Assertions
    assert response["report_type"] == "profit_loss"
    assert response["period"]["start_date"] == start_date
    assert response["period"]["end_date"] == end_date
    assert "data" in response
    assert "revenue" in response["data"]
    assert "expenses" in response["data"]
    assert "net_income" in response["data"]
    assert "generated_at" in response


@pytest.mark.asyncio
async def test_generate_report_balance_sheet(odoo_mcp_client):
    """Test balance sheet report generation."""
    result = await odoo_mcp_client.call_tool(
        "generate_report",
        arguments={
            "report_type": "balance_sheet",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["report_type"] == "balance_sheet"
    assert "data" in response


@pytest.mark.asyncio
async def test_generate_report_cash_flow(odoo_mcp_client):
    """Test cash flow report generation."""
    result = await odoo_mcp_client.call_tool(
        "generate_report",
        arguments={
            "report_type": "cash_flow",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["report_type"] == "cash_flow"


@pytest.mark.asyncio
async def test_generate_report_aged_receivables(odoo_mcp_client):
    """Test aged receivables report generation."""
    result = await odoo_mcp_client.call_tool(
        "generate_report",
        arguments={
            "report_type": "aged_receivables",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["report_type"] == "aged_receivables"


@pytest.mark.asyncio
async def test_generate_report_invalid_type(odoo_mcp_client):
    """Test report generation with invalid type."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "generate_report",
            arguments={
                "report_type": "invalid_report_type",
                "start_date": "2026-01-01",
                "end_date": "2026-01-31"
            }
        )
    assert "report" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_generate_report_invalid_date_range(odoo_mcp_client):
    """Test report generation with invalid date range (start after end)."""
    with pytest.raises(Exception) as exc_info:
        await odoo_mcp_client.call_tool(
            "generate_report",
            arguments={
                "report_type": "profit_loss",
                "start_date": "2026-02-01",  # After end date
                "end_date": "2026-01-31"
            }
        )
    assert "date" in str(exc_info.value).lower() or "range" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_generate_report_pdf_format(odoo_mcp_client):
    """Test report generation in PDF format."""
    result = await odoo_mcp_client.call_tool(
        "generate_report",
        arguments={
            "report_type": "profit_loss",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "format": "pdf"
        }
    )

    response = json.loads(result.content[0].text)
    # In DRY_RUN mode, PDF generation is simulated
    assert "report_type" in response


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_invoice_workflow(odoo_mcp_client):
    """Test complete invoice workflow: create → send → record payment."""
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    # Step 1: Create invoice
    create_result = await odoo_mcp_client.call_tool(
        "create_invoice",
        arguments={
            "customer_name": "Integration Test Customer",
            "customer_email": "integration@test.com",
            "invoice_date": today,
            "due_date": due_date,
            "line_items": [
                {"description": "Service", "quantity": 1, "unit_price": 1000.00}
            ]
        }
    )

    create_response = json.loads(create_result.content[0].text)
    invoice_id = create_response["invoice_id"]

    # Step 2: Send invoice
    send_result = await odoo_mcp_client.call_tool(
        "send_invoice",
        arguments={"invoice_id": invoice_id}
    )

    send_response = json.loads(send_result.content[0].text)
    assert send_response["email_sent"] is True

    # Step 3: Record payment
    payment_result = await odoo_mcp_client.call_tool(
        "record_payment",
        arguments={
            "invoice_id": invoice_id,
            "amount": 1000.00,
            "payment_date": today,
            "payment_method": "bank_transfer"
        }
    )

    payment_response = json.loads(payment_result.content[0].text)
    assert payment_response["invoice_status"] == "paid"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
