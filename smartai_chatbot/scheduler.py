"""
Scheduler - Background jobs for reports, alerts, and maintenance
"""

import frappe
import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


def send_daily_reports():
    """Send daily reports to users"""
    try:
        # Get all users with daily report preference
        users = frappe.db.get_list(
            "User",
            filters={"enabled": 1},
            fields=["name", "email"],
            limit_page_length=1000
        )
        
        for user in users:
            try:
                # Generate daily summary
                summary = generate_daily_summary(user.get("name"))
                
                # Send email
                send_email(
                    recipients=user.get("email"),
                    subject=f"SmartAI Daily Report - {frappe.utils.today()}",
                    message=format_daily_report(summary)
                )
                
                logger.info(f"Daily report sent to {user.get('email')}")
            
            except Exception as e:
                logger.error(f"Error sending report to {user.get('email')}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in send_daily_reports: {str(e)}")
        frappe.log_error(f"Daily Reports Error: {str(e)}", "Scheduler Error")


def generate_daily_summary(user: str) -> Dict:
    """Generate daily summary for user"""
    try:
        date_from = frappe.utils.add_days(frappe.utils.today(), -1)
        
        summary = {
            "user": user,
            "date": frappe.utils.today(),
            "sales_orders": frappe.db.count(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ]
            ),
            "total_sales": frappe.db.get_value(
                "Sales Order",
                filters=[
                    ["creation", ">=", date_from],
                    ["status", "!=", "Cancelled"]
                ],
                fieldname="SUM(grand_total)"
            ) or 0,
            "pending_invoices": frappe.db.count(
                "Sales Invoice",
                filters=[["status", "=", "Open"]]
            ),
            "low_stock_items": frappe.db.count(
                "Item",
                filters=[
                    ["reorder_level", ">", 0],
                    ["stock_qty", "<", "reorder_level"]
                ]
            ),
        }
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating daily summary: {str(e)}")
        return {}


def format_daily_report(summary: Dict) -> str:
    """Format daily report for email"""
    return f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #1f4788; color: white; padding: 20px; }}
        .content {{ padding: 20px; }}
        .metric {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
    </style></head>
    <body>
        <div class="header">
            <h2>SmartAI Daily Report</h2>
            <p>Date: {summary.get('date', 'N/A')}</p>
        </div>
        <div class="content">
            <div class="metric">
                <strong>Sales Orders:</strong> {summary.get('sales_orders', 0)}
            </div>
            <div class="metric">
                <strong>Total Sales:</strong> Rs. {summary.get('total_sales', 0):,.2f}
            </div>
            <div class="metric">
                <strong>Pending Invoices:</strong> {summary.get('pending_invoices', 0)}
            </div>
            <div class="metric">
                <strong>Low Stock Items:</strong> {summary.get('low_stock_items', 0)}
            </div>
        </div>
    </body>
    </html>
    """


def send_email(recipients: str, subject: str, message: str):
    """Send email notification"""
    try:
        from frappe.email.queue import send
        
        send(
            recipients=[recipients],
            subject=subject,
            message=message,
        )
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


def check_low_stock_alerts():
    """Check for low stock items and notify"""
    try:
        low_stock = frappe.db.sql("""
            SELECT item_code, item_name, stock_qty, reorder_level,
                   (reorder_level - stock_qty) as shortage
            FROM `tabItem`
            WHERE reorder_level > 0
            AND stock_qty < reorder_level
            AND disabled = 0
        """, as_dict=True)
        
        if low_stock:
            # Create notification
            notification = frappe.get_doc({
                "doctype": "Notification",
                "title": f"Low Stock Alert - {len(low_stock)} items",
                "message": f"<p>{len(low_stock)} items have low stock:</p>" +
                          "".join([f"<p>- {item['item_code']}: {item['shortage']} units short</p>"
                                  for item in low_stock[:10]]),
                "alert_type": "Info",
            })
            notification.insert()
            
            logger.info(f"Low stock alert created for {len(low_stock)} items")
    
    except Exception as e:
        logger.error(f"Error checking low stock: {str(e)}")


def cleanup_old_sessions():
    """Clean up old chat sessions"""
    try:
        cutoff_date = frappe.utils.add_days(frappe.utils.today(), -30)
        
        old_sessions = frappe.db.get_list(
            "Chat Session",
            filters=[
                ["modified", "<", cutoff_date],
                ["status", "=", "Closed"]
            ],
            fields=["name"],
            limit_page_length=1000
        )
        
        for session in old_sessions:
            # Delete related messages
            frappe.db.delete(
                "Chat Message",
                {"chat_session": session.get("name")}
            )
            
            # Delete session
            frappe.delete_doc("Chat Session", session.get("name"))
        
        logger.info(f"Cleaned up {len(old_sessions)} old chat sessions")
    
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")


def sync_ai_usage():
    """Sync AI usage statistics"""
    try:
        # Get usage from last hour
        date_from = frappe.utils.add_hours(frappe.utils.now(), -1)
        
        usage_logs = frappe.db.get_list(
            "AI Usage Log",
            filters=[["timestamp", ">=", date_from]],
            fields=["provider_name", "COUNT(*) as count"],
            group_by="provider_name"
        )
        
        # Update provider statistics
        for log in usage_logs:
            try:
                config = frappe.get_doc("AI API Configuration", log.get("provider_name"))
                config.total_requests = (config.total_requests or 0) + log.get("count", 0)
                config.save()
            except:
                pass
        
        logger.info(f"Synced AI usage statistics from {len(usage_logs)} providers")
    
    except Exception as e:
        logger.error(f"Error syncing AI usage: {str(e)}")


def process_autonomous_actions():
    """Process pending autonomous actions"""
    try:
        pending_actions = frappe.db.get_list(
            "Autonomous Action",
            filters=[["status", "=", "Pending"]],
            fields=["name", "action_type", "data"],
            limit_page_length=100
        )
        
        for action in pending_actions:
            try:
                process_action(action)
            except Exception as e:
                logger.error(f"Error processing action {action.get('name')}: {str(e)}")
        
        logger.info(f"Processed {len(pending_actions)} autonomous actions")
    
    except Exception as e:
        logger.error(f"Error in process_autonomous_actions: {str(e)}")


def process_action(action: Dict):
    """Process a single autonomous action"""
    try:
        action_type = action.get("action_type")
        data = frappe.parse_json(action.get("data", "{}"))
        
        if action_type == "create_sales_order":
            from smartai_chatbot.autonomous_agent import AutomatedDataEntry
            entry = AutomatedDataEntry()
            result = entry.create_sales_order(data, auto_submit=False)
            
            status = "Completed" if result.get("success") else "Failed"
            frappe.db.set_value("Autonomous Action", action.get("name"), "status", status)
        
        elif action_type == "send_email":
            from smartai_chatbot.export_manager import ExportManager
            manager = ExportManager()
            result = manager.send_report_email(
                data.get("recipients"),
                data.get("subject"),
                data.get("message"),
                data.get("file_path")
            )
            
            status = "Completed" if result.get("success") else "Failed"
            frappe.db.set_value("Autonomous Action", action.get("name"), "status", status)
    
    except Exception as e:
        logger.error(f"Error processing action: {str(e)}")
        frappe.db.set_value("Autonomous Action", action.get("name"), "status", "Failed")


# Scheduled event handlers (called by Frappe scheduler)
def on_daily():
    """Called once daily"""
    send_daily_reports()
    check_low_stock_alerts()


def on_hourly():
    """Called hourly"""
    cleanup_old_sessions()
    sync_ai_usage()


def on_all():
    """Called every minute"""
    process_autonomous_actions()
