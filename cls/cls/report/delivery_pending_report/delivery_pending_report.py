# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

#import frappe


#def execute(filters=None):
#	columns, data = [], []
#	return columns, data
import frappe
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    # Set default values if not provided
    today = datetime.today().strftime("%Y-%m-%d")
    financial_start_date = f"{datetime.today().year}-04-01"

    if datetime.today().month < 4:
        financial_start_date = f"{datetime.today().year - 1}-04-01"

    filters.setdefault("from_date", financial_start_date)
    filters.setdefault("to_date", today)

    # Debugging: Log received filters (Fixing the logging issue)
    frappe.log_error(frappe.as_json(filters), "Delivery Pending Report Filters")

    # Constructing WHERE conditions dynamically based on filters
    conditions = ["so.docstatus = 1", "so.status IN ('To Deliver and Bill', 'To Deliver','Partly Delivered')"]
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("so.transaction_date BETWEEN %(from_date)s AND %(to_date)s")
    
    if filters.get("sales_partner"):
        conditions.append("so.sales_partner = %(sales_partner)s")
    
    if filters.get("customer"):
        conditions.append("so.customer = %(customer)s")
    
    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
        CONCAT('<input type="checkbox" class="select-checkbox" data-order="', so.name, '" data-item="', soi.item_code, '" data-qty="', (soi.qty - IFNULL(SUM(dni.qty), 0)), '">') AS `CheckBox`,
        so.transaction_date AS `Date`,
        so.name AS `Sales Order No`,
        so.sales_partner AS `Agent Name`,
        so.customer AS `Customer Name`,
        soi.item_group AS `Group Name`,
        soi.display_item_name AS `Product Name`,
        soi.description AS `Item Description`,
        (soi.qty - IFNULL(SUM(dni.qty), 0)) AS `No of Bales`,
        soi.conversion_factor AS `Unit per Bale`,
        ((soi.qty - IFNULL(SUM(dni.qty), 0)) * soi.conversion_factor) AS `Quantity`
    FROM
        `tabSales Order` so
    JOIN
        `tabSales Order Item` soi ON soi.parent = so.name
    LEFT JOIN
        `tabDelivery Note` dn ON dn.against_sales_order = so.name AND dn.docstatus < 2
    LEFT JOIN
        `tabDelivery Note Item` dni ON dni.parent = dn.name AND dni.item_code = soi.item_code
    WHERE
        {where_clause}
    GROUP BY
        soi.name
    HAVING
        `No of Bales` > 0
    ORDER BY
        so.transaction_date DESC;
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    columns = [
        {"label": "Select", "fieldname": "CheckBox", "fieldtype": "HTML", "width": 50},
        {"label": "Date", "fieldname": "Date", "fieldtype": "Date", "width": 120},
        {"label": "Sales Order No", "fieldname": "Sales Order No", "fieldtype": "Data", "width": 150},
        {"label": "Agent Name", "fieldname": "Agent Name", "fieldtype": "Link", "options": "Sales Partner", "width": 150},
        {"label": "Customer Name", "fieldname": "Customer Name", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Group Name", "fieldname": "Group Name", "fieldtype": "Data", "width": 120},
        {"label": "Product Name", "fieldname": "Product Name", "fieldtype": "Data", "width": 150},
        {"label": "Item Description", "fieldname": "Item Description", "fieldtype": "Data", "width": 200},
        {"label": "No of Bales", "fieldname": "No of Bales", "fieldtype": "Float", "width": 100},
        {"label": "Unit per Bale", "fieldname": "Unit per Bale", "fieldtype": "Float", "width": 120},
        {"label": "Quantity", "fieldname": "Quantity", "fieldtype": "Float", "width": 120},
    ]

    return columns, data
