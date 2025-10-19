"""
Autonomous Agent - Auto-process documents, extract data, and create ERPNext records
"""

import frappe
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import base64
import io

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Extract data from documents (PDF, images, CSV)"""
    
    @staticmethod
    def extract_from_image(image_data: str) -> Dict:
        """Extract text from image using OCR"""
        try:
            from PIL import Image
            import pytesseract
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR
            text = pytesseract.image_to_string(image)
            
            return {
                "success": True,
                "text": text,
                "confidence": 0.9
            }
        
        except Exception as e:
            logger.error(f"Image extraction error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> Dict:
        """Extract text from PDF"""
        try:
            import PyPDF2
            
            text_data = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_data.append(page.extract_text())
            
            return {
                "success": True,
                "text": "\n".join(text_data),
                "pages": len(text_data)
            }
        
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def extract_from_csv(csv_path: str) -> Dict:
        """Extract data from CSV"""
        try:
            import csv
            
            data = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            
            return {
                "success": True,
                "data": data,
                "rows": len(data)
            }
        
        except Exception as e:
            logger.error(f"CSV extraction error: {str(e)}")
            return {"success": False, "error": str(e)}


class DataValidator:
    """Validate and clean extracted data"""
    
    @staticmethod
    def validate_sales_order(data: Dict) -> Tuple[bool, List[str]]:
        """Validate sales order data"""
        errors = []
        
        if not data.get("customer"):
            errors.append("Customer is required")
        elif not frappe.db.exists("Customer", data["customer"]):
            errors.append(f"Customer '{data['customer']}' not found")
        
        if not data.get("items"):
            errors.append("At least one item is required")
        
        for item in data.get("items", []):
            if not frappe.db.exists("Item", item.get("item_code")):
                errors.append(f"Item '{item.get('item_code')}' not found")
        
        if data.get("grand_total", 0) <= 0:
            errors.append("Grand total must be greater than 0")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_purchase_order(data: Dict) -> Tuple[bool, List[str]]:
        """Validate purchase order data"""
        errors = []
        
        if not data.get("supplier"):
            errors.append("Supplier is required")
        elif not frappe.db.exists("Supplier", data["supplier"]):
            errors.append(f"Supplier '{data['supplier']}' not found")
        
        if not data.get("items"):
            errors.append("At least one item is required")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_invoice(data: Dict) -> Tuple[bool, List[str]]:
        """Validate invoice data"""
        errors = []
        
        if not data.get("customer"):
            errors.append("Customer is required")
        
        if not data.get("items"):
            errors.append("At least one item is required")
        
        return len(errors) == 0, errors


class AutomatedDataEntry:
    """Automatically create ERPNext records"""
    
    @staticmethod
    def create_sales_order(data: Dict, auto_submit: bool = False) -> Dict:
        """Create Sales Order from extracted data"""
        try:
            # Validate
            is_valid, errors = DataValidator.validate_sales_order(data)
            if not is_valid:
                return {"success": False, "errors": errors}
            
            # Create SO
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "customer": data["customer"],
                "transaction_date": data.get("transaction_date", frappe.utils.today()),
                "delivery_date": data.get("delivery_date"),
                "items": data.get("items", []),
            })
            
            so.insert()
            
            if auto_submit:
                so.submit()
            
            return {
                "success": True,
                "doctype": "Sales Order",
                "name": so.name,
                "message": f"Sales Order {so.name} created successfully"
            }
        
        except Exception as e:
            logger.error(f"Error creating SO: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def create_purchase_order(data: Dict, auto_submit: bool = False) -> Dict:
        """Create Purchase Order from extracted data"""
        try:
            # Validate
            is_valid, errors = DataValidator.validate_purchase_order(data)
            if not is_valid:
                return {"success": False, "errors": errors}
            
            # Create PO
            po = frappe.get_doc({
                "doctype": "Purchase Order",
                "supplier": data["supplier"],
                "transaction_date": data.get("transaction_date", frappe.utils.today()),
                "items": data.get("items", []),
            })
            
            po.insert()
            
            if auto_submit:
                po.submit()
            
            return {
                "success": True,
                "doctype": "Purchase Order",
                "name": po.name,
                "message": f"Purchase Order {po.name} created successfully"
            }
        
        except Exception as e:
            logger.error(f"Error creating PO: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def create_customer(data: Dict) -> Dict:
        """Create new Customer"""
        try:
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": data.get("name"),
                "customer_type": data.get("customer_type", "Individual"),
                "territory": data.get("territory"),
                "customer_group": data.get("customer_group"),
            })
            
            customer.insert()
            
            return {
                "success": True,
                "doctype": "Customer",
                "name": customer.name,
                "message": f"Customer {customer.name} created successfully"
            }
        
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return {"success": False, "error": str(e)}


class AutonomousAgent:
    """Main autonomous agent orchestrator"""
    
    def __init__(self):
        self.extractor = DocumentExtractor()
        self.validator = DataValidator()
        self.entry = AutomatedDataEntry()
    
    @frappe.whitelist()
    def process_document(self, file_path: str, document_type: str,
                        auto_create: bool = False) -> Dict:
        """Process document and optionally auto-create records"""
        
        try:
            # Determine file type
            if file_path.endswith('.pdf'):
                extract_result = self.extractor.extract_from_pdf(file_path)
            elif file_path.endswith(('.png', '.jpg', '.jpeg')):
                with open(file_path, 'rb') as f:
                    extract_result = self.extractor.extract_from_image(
                        base64.b64encode(f.read()).decode()
                    )
            elif file_path.endswith('.csv'):
                extract_result = self.extractor.extract_from_csv(file_path)
            else:
                return {"success": False, "error": "Unsupported file type"}
            
            if not extract_result.get("success"):
                return extract_result
            
            # Parse extracted data
            extracted_data = self._parse_extracted_data(
                extract_result, document_type
            )
            
            # Validate
            if document_type == "Sales Order":
                is_valid, errors = self.validator.validate_sales_order(extracted_data)
            elif document_type == "Purchase Order":
                is_valid, errors = self.validator.validate_purchase_order(extracted_data)
            else:
                is_valid = True
                errors = []
            
            if not is_valid:
                return {
                    "success": False,
                    "errors": errors,
                    "extracted_data": extracted_data
                }
            
            # Auto-create if enabled
            if auto_create:
                if document_type == "Sales Order":
                    return self.entry.create_sales_order(extracted_data, auto_submit=False)
                elif document_type == "Purchase Order":
                    return self.entry.create_purchase_order(extracted_data, auto_submit=False)
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "ready_for_creation": is_valid,
                "message": f"Document processed. {len(errors)} validation errors."
            }
        
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_extracted_data(self, extraction: Dict, doctype: str) -> Dict:
        """Parse extracted data using AI"""
        # This would use the AI gateway to parse structured data
        # For now, return basic structure
        
        if doctype == "Sales Order":
            return {
                "customer": "",
                "transaction_date": frappe.utils.today(),
                "items": [],
                "grand_total": 0
            }
        
        return extraction
    
    @frappe.whitelist()
    def confirm_and_create(self, extracted_data: Dict, document_type: str) -> Dict:
        """Confirm extracted data and create record"""
        
        try:
            if document_type == "Sales Order":
                return self.entry.create_sales_order(extracted_data, auto_submit=False)
            elif document_type == "Purchase Order":
                return self.entry.create_purchase_order(extracted_data, auto_submit=False)
            else:
                return {"success": False, "error": f"Unsupported document type: {document_type}"}
        
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            return {"success": False, "error": str(e)}


# Public API endpoints
@frappe.whitelist()
def process_document(file_path, document_type, auto_create=False):
    agent = AutonomousAgent()
    return agent.process_document(file_path, document_type, auto_create)


@frappe.whitelist()
def confirm_and_create(extracted_data, document_type):
    agent = AutonomousAgent()
    extracted_data = json.loads(extracted_data) if isinstance(extracted_data, str) else extracted_data
    return agent.confirm_and_create(extracted_data, document_type)
