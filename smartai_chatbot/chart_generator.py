"""
Chart Generator - Create interactive visualizations from ERPNext data
"""

import frappe
import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate interactive charts using Plotly and Chart.js configurations"""
    
    @frappe.whitelist()
    def generate_sales_trend(self, days: int = 30) -> Dict:
        """Generate sales trend line chart"""
        try:
            date_from = frappe.utils.add_days(frappe.utils.today(), -days)
            
            sales_data = frappe.db.sql(f"""
                SELECT DATE(creation) as date, SUM(grand_total) as total, COUNT(*) as count
                FROM `tabSales Order`
                WHERE DATE(creation) >= DATE('{date_from}')
                AND status != 'Cancelled'
                GROUP BY DATE(creation)
                ORDER BY date ASC
            """, as_dict=True)
            
            dates = [item['date'].strftime('%Y-%m-%d') for item in sales_data]
            totals = [float(item['total'] or 0) for item in sales_data]
            
            return {
                "type": "line",
                "title": f"Sales Trend ({days} Days)",
                "labels": dates,
                "datasets": [{
                    "label": "Sales Amount",
                    "data": totals,
                    "borderColor": "rgb(75, 192, 192)",
                    "tension": 0.1,
                    "fill": False,
                }]
            }
        
        except Exception as e:
            logger.error(f"Error generating sales trend: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def generate_top_customers(self, limit: int = 10, days: int = 30) -> Dict:
        """Generate top customers pie/bar chart"""
        try:
            date_from = frappe.utils.add_days(frappe.utils.today(), -days)
            
            customers = frappe.db.sql(f"""
                SELECT customer, SUM(grand_total) as total, COUNT(*) as order_count
                FROM `tabSales Order`
                WHERE DATE(creation) >= DATE('{date_from}')
                AND status != 'Cancelled'
                GROUP BY customer
                ORDER BY total DESC
                LIMIT {limit}
            """, as_dict=True)
            
            return {
                "type": "pie",
                "title": f"Top {limit} Customers",
                "labels": [c['customer'] for c in customers],
                "datasets": [{
                    "label": "Sales Amount",
                    "data": [float(c['total'] or 0) for c in customers],
                    "backgroundColor": [
                        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
                        "#FF9F40", "#FF6384", "#C9CBCF", "#4BC0C0", "#FF6384"
                    ]
                }]
            }
        
        except Exception as e:
            logger.error(f"Error generating top customers: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def generate_inventory_status(self, limit: int = 15) -> Dict:
        """Generate inventory status bar chart"""
        try:
            items = frappe.db.get_list(
                "Item",
                fields=["item_code", "item_name", "stock_qty", "reorder_level"],
                filters=[["disabled", "=", 0]],
                limit_page_length=limit,
                order_by="stock_qty asc"
            )
            
            return {
                "type": "bar",
                "title": f"Inventory Status (Low Stock Items)",
                "labels": [f"{item['item_code']}" for item in items],
                "datasets": [
                    {
                        "label": "Current Stock",
                        "data": [float(item['stock_qty'] or 0) for item in items],
                        "backgroundColor": "rgba(75, 192, 192, 0.7)",
                    },
                    {
                        "label": "Reorder Level",
                        "data": [float(item['reorder_level'] or 0) for item in items],
                        "backgroundColor": "rgba(255, 99, 132, 0.7)",
                    }
                ]
            }
        
        except Exception as e:
            logger.error(f"Error generating inventory status: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def generate_revenue_by_period(self, days: int = 90) -> Dict:
        """Generate revenue comparison by period"""
        try:
            # Weekly revenue
            revenue_data = frappe.db.sql(f"""
                SELECT 
                    DATE_FORMAT(creation, '%Y-W%w') as week,
                    SUM(grand_total) as total
                FROM `tabSales Order`
                WHERE DATE(creation) >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
                AND status != 'Cancelled'
                GROUP BY WEEK(creation)
                ORDER BY week
            """, as_dict=True)
            
            weeks = [f"Week {data['week'][-2:]}" for data in revenue_data]
            totals = [float(data['total'] or 0) for data in revenue_data]
            
            return {
                "type": "bar",
                "title": f"Weekly Revenue ({days} Days)",
                "labels": weeks,
                "datasets": [{
                    "label": "Revenue",
                    "data": totals,
                    "backgroundColor": "rgba(54, 162, 235, 0.7)",
                }]
            }
        
        except Exception as e:
            logger.error(f"Error generating revenue chart: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def generate_order_status_distribution(self) -> Dict:
        """Generate order status distribution"""
        try:
            statuses = frappe.db.sql("""
                SELECT status, COUNT(*) as count
                FROM `tabSales Order`
                WHERE YEAR(creation) = YEAR(NOW())
                GROUP BY status
            """, as_dict=True)
            
            return {
                "type": "doughnut",
                "title": "Sales Order Status Distribution",
                "labels": [s['status'] for s in statuses],
                "datasets": [{
                    "label": "Count",
                    "data": [s['count'] for s in statuses],
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.7)",
                        "rgba(54, 162, 235, 0.7)",
                        "rgba(255, 206, 86, 0.7)",
                        "rgba(75, 192, 192, 0.7)",
                    ]
                }]
            }
        
        except Exception as e:
            logger.error(f"Error generating status chart: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def generate_payment_status(self) -> Dict:
        """Generate payment status chart"""
        try:
            invoices = frappe.db.sql("""
                SELECT status, COUNT(*) as count, SUM(grand_total) as total
                FROM `tabSales Invoice`
                WHERE YEAR(posting_date) = YEAR(NOW())
                GROUP BY status
            """, as_dict=True)
            
            return {
                "type": "pie",
                "title": "Invoice Status",
                "labels": [inv['status'] for inv in invoices],
                "datasets": [{
                    "label": "Amount",
                    "data": [float(inv['total'] or 0) for inv in invoices],
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.7)",
                        "rgba(54, 162, 235, 0.7)",
                        "rgba(255, 206, 86, 0.7)",
                    ]
                }]
            }
        
        except Exception as e:
            logger.error(f"Error generating payment chart: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def generate_custom_chart(self, doctype: str, field_x: str, field_y: str,
                            aggregation: str = "sum", filters: Dict = None) -> Dict:
        """Generate custom chart from any doctype"""
        try:
            filters = filters or {}
            
            query = f"""
                SELECT {field_x}, {aggregation.upper()}({field_y}) as value
                FROM `tab{doctype}`
                WHERE 1=1
            """
            
            for key, value in filters.items():
                if isinstance(value, str):
                    query += f" AND {key} = '{value}'"
                else:
                    query += f" AND {key} = {value}"
            
            query += f" GROUP BY {field_x}"
            
            data = frappe.db.sql(query, as_dict=True)
            
            return {
                "type": "bar",
                "title": f"{field_y} by {field_x}",
                "labels": [row[field_x] for row in data],
                "datasets": [{
                    "label": field_y,
                    "data": [float(row['value'] or 0) for row in data],
                    "backgroundColor": "rgba(75, 192, 192, 0.7)",
                }]
            }
        
        except Exception as e:
            logger.error(f"Error generating custom chart: {str(e)}")
            return {"error": str(e)}


# Public API endpoints
@frappe.whitelist()
def generate_sales_trend(days=30):
    generator = ChartGenerator()
    return generator.generate_sales_trend(days)


@frappe.whitelist()
def generate_top_customers(limit=10, days=30):
    generator = ChartGenerator()
    return generator.generate_top_customers(limit, days)


@frappe.whitelist()
def generate_inventory_status(limit=15):
    generator = ChartGenerator()
    return generator.generate_inventory_status(limit)


@frappe.whitelist()
def generate_revenue_by_period(days=90):
    generator = ChartGenerator()
    return generator.generate_revenue_by_period(days)
