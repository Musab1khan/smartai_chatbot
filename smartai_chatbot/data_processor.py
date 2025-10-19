"""
Data Processor - Real-time ERPNext data retrieval and processing
"""

import frappe
import pandas as pd
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handle data retrieval from ERPNext"""
    
    @frappe.whitelist()
    def get_sales_data(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Fetch sales orders data"""
        try:
            date_from = frappe.utils.add_days(frappe.utils.today(), -days)
            
            return frappe.db.get_list(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ],
                fields=[
                    "name", "customer", "grand_total", "status",
                    "creation", "delivery_date", "transaction_date"
                ],
                limit_page_length=limit,
                order_by="creation desc"
            )
        except Exception as e:
            logger.error(f"Error fetching sales data: {str(e)}")
            return []
    
    @frappe.whitelist()
    def get_purchase_data(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Fetch purchase orders data"""
        try:
            date_from = frappe.utils.add_days(frappe.utils.today(), -days)
            
            return frappe.db.get_list(
                "Purchase Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ],
                fields=[
                    "name", "supplier", "grand_total", "status",
                    "creation", "expected_delivery_date"
                ],
                limit_page_length=limit,
                order_by="creation desc"
            )
        except Exception as e:
            logger.error(f"Error fetching purchase data: {str(e)}")
            return []
    
    @frappe.whitelist()
    def get_inventory_status(self, limit: int = 20) -> List[Dict]:
        """Get inventory/stock status"""
        try:
            return frappe.db.get_list(
                "Item",
                fields=[
                    "item_code", "item_name", "stock_qty",
                    "reorder_level", "valuation_rate"
                ],
                filters=[["disabled", "=", 0]],
                limit_page_length=limit,
                order_by="stock_qty asc"
            )
        except Exception as e:
            logger.error(f"Error fetching inventory: {str(e)}")
            return []
    
    @frappe.whitelist()
    def get_customer_list(self, limit: int = 20) -> List[Dict]:
        """Get customer information"""
        try:
            return frappe.db.get_list(
                "Customer",
                fields=["name", "customer_name", "territory", "customer_group", "credit_limit"],
                filters=[["disabled", "=", 0]],
                limit_page_length=limit
            )
        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            return []
    
    @frappe.whitelist()
    def get_supplier_list(self, limit: int = 20) -> List[Dict]:
        """Get supplier information"""
        try:
            return frappe.db.get_list(
                "Supplier",
                fields=["name", "supplier_name", "country", "supplier_group"],
                filters=[["disabled", "=", 0]],
                limit_page_length=limit
            )
        except Exception as e:
            logger.error(f"Error fetching suppliers: {str(e)}")
            return []
    
    @frappe.whitelist()
    def get_pending_invoices(self, limit: int = 10) -> List[Dict]:
        """Get pending invoices"""
        try:
            return frappe.db.get_list(
                "Sales Invoice",
                filters=[["status", "=", "Open"]],
                fields=["name", "customer", "grand_total", "due_date"],
                limit_page_length=limit,
                order_by="due_date asc"
            )
        except Exception as e:
            logger.error(f"Error fetching invoices: {str(e)}")
            return []
    
    @frappe.whitelist()
    def get_sales_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get sales summary for dashboard"""
        try:
            date_from = frappe.utils.add_days(frappe.utils.today(), -days)
            
            total_sales = frappe.db.get_value(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ],
                fieldname="SUM(grand_total)"
            ) or 0
            
            order_count = frappe.db.count(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ]
            )
            
            top_customers = frappe.db.sql(f"""
                SELECT customer, COUNT(*) as count, SUM(grand_total) as total
                FROM `tabSales Order`
                WHERE DATE(creation) >= DATE('{date_from}')
                AND status != 'Cancelled'
                GROUP BY customer
                ORDER BY total DESC
                LIMIT 5
            """, as_dict=True)
            
            return {
                "total_sales": total_sales,
                "order_count": order_count,
                "period_days": days,
                "top_customers": top_customers,
                "average_order_value": total_sales / max(order_count, 1)
            }
        
        except Exception as e:
            logger.error(f"Error generating sales summary: {str(e)}")
            return {}
    
    @frappe.whitelist()
    def get_low_stock_items(self, limit: int = 10) -> List[Dict]:
        """Get items with low stock"""
        try:
            return frappe.db.sql(f"""
                SELECT item_code, item_name, stock_qty, reorder_level,
                       (reorder_level - stock_qty) as shortage
                FROM `tabItem`
                WHERE reorder_level > 0
                AND stock_qty < reorder_level
                AND disabled = 0
                ORDER BY shortage DESC
                LIMIT {limit}
            """, as_dict=True)
        
        except Exception as e:
            logger.error(f"Error fetching low stock items: {str(e)}")
            return []
    
    @frappe.whitelist()
    def export_to_dataframe(self, doctype: str, filters: Dict = None) -> Dict:
        """Export data to pandas dataframe (for analysis)"""
        try:
            filters = filters or {}
            docs = frappe.get_list(doctype, filters=filters, limit_page_length=1000)
            df = pd.DataFrame(docs)
            
            return {
                "success": True,
                "rows": len(df),
                "columns": df.columns.tolist(),
                "data": df.to_dict('records')[:100]  # First 100 rows
            }
        
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return {"success": False, "error": str(e)}


# Public API endpoints
@frappe.whitelist()
def get_sales_data(days=30, limit=10):
    processor = DataProcessor()
    return processor.get_sales_data(days, limit)


@frappe.whitelist()
def get_inventory_status(limit=20):
    processor = DataProcessor()
    return processor.get_inventory_status(limit)


@frappe.whitelist()
def get_sales_summary(days=30):
    processor = DataProcessor()
    return processor.get_sales_summary(days)


@frappe.whitelist()
def get_low_stock_items(limit=10):
    processor = DataProcessor()
    return processor.get_low_stock_items(limit)
