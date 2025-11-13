// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

//frappe.query_reports["delivery pending report"] = {
//	"filters": [
//
//	]
//};






frappe.query_reports["delivery pending report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "sales_partner",
            "label": __("Agent"),
            "fieldtype": "Link",
            "options": "Sales Partner"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        }
    ],

    onload: function(report) {
        if (!report.custom_button_added) {
            report.page.add_inner_button(__('Create Delivery Note'), function() {
                let selected_orders = [];

                // Loop through selected checkboxes and collect relevant data
                $(".select-checkbox:checked").each(function() {
                    let sales_order_no = $(this).data("order");
                    let item_code = $(this).data("item");
                    let qty = parseFloat($(this).data("qty"));

                    if (sales_order_no && item_code && qty > 0) {
                        selected_orders.push({
                            sales_order: sales_order_no,
                            item_code: item_code,
                            qty: qty,
                            // uom:uom
                        });
                    }
                });

                if (selected_orders.length === 0) {
                    frappe.msgprint(__('Please select at least one Sales Order.'));
                    return;
                }
                frappe.call({
                    method: "erpnext.stock.doctype.delivery_note.delivery_note.create_delivery_note_from_sales_orders",
                    args: { sales_orders: selected_orders },
                    callback: function(response) {
                        console.log(response.message);
                        if (response.message && response.message.length > 0) {
                            frappe.msgprint({
                                title: __('Success'),
                                message: __('Delivery Notes Created: ') + response.message.join(", "),
                                indicator: 'green'
                            });

                            report.refresh();
                        } else {
                            frappe.msgprint({
                                title: __('Error'),
                                message: __('No Delivery Notes were created.'),
                                indicator: 'red'
                            });
                        }
                    }
                });
            });

            report.custom_button_added = true;
        }
    }
};
