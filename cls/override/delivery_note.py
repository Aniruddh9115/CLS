import frappe
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote

class CustomeDeliveryNote(DeliveryNote):
    def on_submit(self):
        super().on_submit()
        self.update_sales_order_status

    def update_sales_order_status(self):
    """Updates the Sales Order status when Delivery Note is submitted"""
    
    if not self.against_sales_order:
        return  # No linked Sales Order, exit function

    sales_order = frappe.get_doc("Sales Order", self.against_sales_order)

    all_items_fully_delivered = True  # Flag to check if all items are fully delivered

    for so_item in sales_order.items:
        # Get total delivered quantity for this item from Delivery Note Items
        delivered_qty = frappe.db.sql("""
            SELECT SUM(qty) FROM `tabDelivery Note Item` 
            WHERE item_code = %s AND docstatus = 1
            AND parent IN (SELECT name FROM `tabDelivery Note` WHERE against_sales_order = %s)
        """, (so_item.item_code, self.against_sales_order))[0][0] or 0

        if delivered_qty < so_item.qty:
            all_items_fully_delivered = False  # If any item is pending, mark as False

    # Update status based on delivered quantity
    new_status = "Completed" if all_items_fully_delivered else "Partly Delivered"

    if sales_order.status != new_status:
        sales_order.db_set("status", new_status)
        frappe.db.commit()
