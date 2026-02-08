#!/usr/bin/env python3
"""
Odoo API Client Library

Provides high-level interface for Odoo operations via MCP server.
Used by workflow scripts for invoice creation, payment recording, etc.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.credentials import CredentialManager
from utils.retry import retry_with_backoff, RetryConfig
from utils.audit_sanitizer import sanitize_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OdooClient:
    """
    High-level Odoo client for accounting operations.

    Wraps Odoo MCP server calls with retry logic, error handling,
    and audit logging.
    """

    def __init__(self, vault_path: str = None):
        """
        Initialize Odoo client.

        Args:
            vault_path: Path to Obsidian vault (default: My_AI_Employee/AI_Employee_Vault/)
        """
        self.vault_path = vault_path or os.path.join(
            Path(__file__).parent.parent.parent.parent,
            "My_AI_Employee",
            "AI_Employee_Vault"
        )
        self.cred_manager = CredentialManager(service_name="ai_employee_odoo")
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        # Retry configuration
        self.retry_config = RetryConfig(
            max_attempts=4,
            backoff_delays=(1.0, 2.0, 4.0, 8.0)
        )

    def _log_operation(self, operation: str, details: Dict[str, Any], result: str = "success"):
        """
        Log operation to audit trail.

        Args:
            operation: Operation type (create_invoice, record_payment, etc.)
            details: Operation details (sanitized)
            result: Operation result (success, failed, queued)
        """
        log_dir = os.path.join(self.vault_path, "Logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": operation,
            "actor": "odoo_client",
            "details": sanitize_credentials(details),
            "result": result
        }

        # Append to JSONL file
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        logger.info(f"Logged {operation}: {result}")

    @retry_with_backoff()
    def create_invoice(
        self,
        customer_name: str,
        customer_email: str,
        line_items: List[Dict[str, Any]],
        invoice_date: str,
        due_date: str,
        tax_rate: float = 0.0,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Create draft invoice in Odoo.

        Args:
            customer_name: Customer name
            customer_email: Customer email
            line_items: List of line items [{"description": str, "quantity": float, "unit_price": float}]
            invoice_date: Invoice date (YYYY-MM-DD)
            due_date: Due date (YYYY-MM-DD)
            tax_rate: Tax rate (0-1, default: 0.0)
            notes: Invoice notes

        Returns:
            Invoice details with invoice_id, status, total_amount, odoo_url
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Creating invoice for {customer_name}")
            result = {
                "invoice_id": f"INV/2026/{datetime.now().strftime('%H%M%S')}",
                "status": "draft",
                "total_amount": sum(item["quantity"] * item["unit_price"] for item in line_items) * (1 + tax_rate),
                "odoo_url": f"http://localhost:8069/web#id=1&model=account.move",
                "created_at": datetime.now().isoformat()
            }
        else:
            # In production, call Odoo MCP server
            # This would use MCP client to call odoo_mcp.py
            raise NotImplementedError("Production Odoo MCP integration pending")

        # Log operation
        self._log_operation(
            "create_invoice",
            {
                "customer_name": customer_name,
                "customer_email": customer_email,
                "invoice_date": invoice_date,
                "due_date": due_date,
                "line_items_count": len(line_items),
                "total_amount": result["total_amount"]
            }
        )

        return result

    @retry_with_backoff()
    def send_invoice(
        self,
        invoice_id: str,
        email_subject: Optional[str] = None,
        email_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send invoice to customer via email.

        Args:
            invoice_id: Odoo invoice ID
            email_subject: Custom email subject (optional)
            email_body: Custom email body (optional)

        Returns:
            Send status with invoice_id, status, email_sent, sent_to, sent_at
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Sending invoice {invoice_id}")
            result = {
                "invoice_id": invoice_id,
                "status": "sent",
                "email_sent": True,
                "sent_to": "customer@example.com",
                "sent_at": datetime.now().isoformat()
            }
        else:
            # In production, call Odoo MCP server
            raise NotImplementedError("Production Odoo MCP integration pending")

        # Log operation
        self._log_operation(
            "send_invoice",
            {
                "invoice_id": invoice_id,
                "email_sent": result["email_sent"]
            }
        )

        return result

    @retry_with_backoff()
    def record_payment(
        self,
        invoice_id: str,
        amount: float,
        payment_date: str,
        payment_method: str,
        reference: str = ""
    ) -> Dict[str, Any]:
        """
        Record payment against invoice.

        Args:
            invoice_id: Odoo invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)
            payment_method: Payment method (bank_transfer, credit_card, cash, check)
            reference: Payment reference/memo

        Returns:
            Payment details with payment_id, invoice_id, status, reconciled, invoice_status
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Recording payment for {invoice_id}: ${amount}")
            result = {
                "payment_id": f"PAY/2026/{datetime.now().strftime('%H%M%S')}",
                "invoice_id": invoice_id,
                "status": "posted",
                "reconciled": True,
                "invoice_status": "paid",
                "created_at": datetime.now().isoformat()
            }
        else:
            # In production, call Odoo MCP server
            raise NotImplementedError("Production Odoo MCP integration pending")

        # Log operation
        self._log_operation(
            "record_payment",
            {
                "invoice_id": invoice_id,
                "amount": amount,
                "payment_method": payment_method,
                "payment_date": payment_date
            }
        )

        return result

    @retry_with_backoff()
    def create_expense(
        self,
        description: str,
        amount: float,
        expense_date: str,
        category: str,
        vendor: Optional[str] = None,
        receipt_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create expense record.

        Args:
            description: Expense description
            amount: Expense amount
            expense_date: Date of expense (YYYY-MM-DD)
            category: Expense category
            vendor: Vendor name (optional)
            receipt_path: Path to receipt file (optional)

        Returns:
            Expense details with expense_id, status, category, receipt_attached
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Creating expense: {description} - ${amount}")
            result = {
                "expense_id": f"EXP/2026/{datetime.now().strftime('%H%M%S')}",
                "status": "draft",
                "category": category,
                "receipt_attached": receipt_path is not None,
                "created_at": datetime.now().isoformat()
            }
        else:
            # In production, call Odoo MCP server
            raise NotImplementedError("Production Odoo MCP integration pending")

        # Log operation
        self._log_operation(
            "create_expense",
            {
                "description": description,
                "amount": amount,
                "category": category,
                "vendor": vendor,
                "expense_date": expense_date
            }
        )

        return result

    @retry_with_backoff()
    def generate_report(
        self,
        report_type: str,
        start_date: str,
        end_date: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate financial report.

        Args:
            report_type: Report type (profit_loss, balance_sheet, cash_flow, aged_receivables)
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            format: Output format (json, pdf)

        Returns:
            Report data with report_type, period, data, generated_at
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Generating {report_type} report for {start_date} to {end_date}")
            result = {
                "report_type": report_type,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "data": {
                    "revenue": 15000.00,
                    "expenses": 8500.00,
                    "net_income": 6500.00,
                    "details": {}
                },
                "generated_at": datetime.now().isoformat()
            }
        else:
            # In production, call Odoo MCP server
            raise NotImplementedError("Production Odoo MCP integration pending")

        # Log operation
        self._log_operation(
            "generate_report",
            {
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "format": format
            }
        )

        return result


if __name__ == "__main__":
    # Test client
    client = OdooClient()

    # Test invoice creation
    invoice = client.create_invoice(
        customer_name="Test Customer",
        customer_email="test@example.com",
        line_items=[
            {"description": "Consulting", "quantity": 1, "unit_price": 1500.00}
        ],
        invoice_date="2026-01-28",
        due_date="2026-02-28"
    )
    print(f"Created invoice: {invoice['invoice_id']}")

    # Test payment recording
    payment = client.record_payment(
        invoice_id=invoice["invoice_id"],
        amount=1500.00,
        payment_date="2026-01-28",
        payment_method="bank_transfer"
    )
    print(f"Recorded payment: {payment['payment_id']}")
