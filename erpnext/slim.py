"""Modules the Clinic360 fork removes (slim ERP, Stage B3), and how a site that had them lets go."""

import frappe


def remove_modules(*modules: str) -> None:
	"""Delete the modules' doctypes, the records tied to them (workspaces, reports, sidebars and so on) and their
	Module Def rows. Tables and their data stay, as when Frappe removes an orphaned doctype.

	Frappe keeps a module dropped from `modules.txt` on purpose and leaves removal to the app, in a patch. Patches run
	before Frappe's own orphan clean-up, so this doesn't wait for it."""
	present = [m for m in modules if frappe.db.exists("Module Def", m)]
	if not present:
		return

	for module in present:
		for doctype in frappe.get_all("DocType", {"module": module, "custom": 0}, pluck="name"):
			frappe.delete_doc("DocType", doctype, ignore_on_trash=True, force=True, ignore_missing=True)

	for doctype, fieldname in linked_doctypes():
		for name in frappe.get_all(doctype, {fieldname: ["in", present]}, pluck="name"):
			frappe.delete_doc(doctype, name, ignore_on_trash=True, force=True, ignore_missing=True)

	for module in present:
		frappe.delete_doc("Module Def", module, ignore_on_trash=True, force=True, ignore_missing=True)


def linked_doctypes() -> list[tuple[str, str]]:
	"""Each doctype that links to Module Def, and the field, for doctypes that still have a table."""
	fields = frappe.get_all(
		"DocField", {"fieldtype": "Link", "options": "Module Def"}, ["parent", "fieldname"]
	)
	single = set(frappe.get_all("DocType", {"issingle": 1}, pluck="name"))
	tables = set(frappe.db.get_tables(cached=False))
	return [
		(f.parent, f.fieldname)
		for f in fields
		if f.parent not in ("DocType", "Module Def") and f.parent not in single and f"tab{f.parent}" in tables
	]
