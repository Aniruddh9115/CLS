import frappe
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def set_indicator(self):
        frappe.throw(self.status)
        self.indicator_color = {
            "Draft": "grey",
            "on Hold": "orange",
            "To Deliver and bill": "purple",
            "To Bill": "blue",
            "To Deliver": "teal",
            "Completed": "green",
            "Cancelled": "red",
            "Partly Delivered": "yellow"
        }.get(self.status, "blue")