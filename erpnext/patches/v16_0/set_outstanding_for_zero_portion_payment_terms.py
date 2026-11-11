import frappe
from frappe.query_builder import DocType


def execute():
	ps = DocType("Payment Schedule")
	for parenttype in ("Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order"):
		parent = DocType(parenttype)
		settled = ps.paid_amount + ps.discounted_amount
		outstanding = ps.payment_amount - settled

		# Select, then update by name: UPDATE ... JOIN is MariaDB-only, and PostgreSQL rejects it.
		rows = (
			frappe.qb.from_(ps)
			.join(parent)
			.on(ps.parent == parent.name)
			.select(
				ps.name,
				outstanding.as_("outstanding"),
				(ps.payment_amount * parent.conversion_rate).as_("base_payment_amount"),
				(outstanding * parent.conversion_rate).as_("base_outstanding"),
			)
			.where(
				(ps.parenttype == parenttype)
				& (parent.docstatus == 1)
				& (ps.invoice_portion == 0)
				& (ps.outstanding == 0)
				& (settled < ps.payment_amount)
			)
		).run(as_dict=True)

		for row in rows:
			name = row.pop("name")
			frappe.db.set_value("Payment Schedule", name, row, update_modified=False)
