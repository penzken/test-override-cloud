import frappe
import json
from frappe.utils import random_string


@frappe.whitelist()
def get_fields_layout(doctype: str, type: str, parent_doctype: str | None = None):
	"""Override to customize the Data Fields layout - replace annual_revenue with deal_value for CRM Deal"""
	from crm.fcrm.doctype.crm_fields_layout.crm_fields_layout import (
		get_default_layout,
		handle_perm_level_restrictions,
	)
	
	tabs = []
	layout = None

	if frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": type}):
		layout = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": type})

	if layout and layout.layout:
		tabs = json.loads(layout.layout)

	if not tabs and type != "Required Fields":
		tabs = get_default_layout(doctype)

	has_tabs = False
	if isinstance(tabs, list) and len(tabs) > 0 and isinstance(tabs[0], dict):
		has_tabs = any("sections" in tab for tab in tabs)

	if not has_tabs:
		tabs = [{"name": "first_tab", "sections": tabs}]

	# CUSTOM OVERRIDE: Replace annual_revenue with deal_value BEFORE processing
	if doctype == "CRM Deal" and type == "Data Fields":
		for tab in tabs:
			for section in tab.get("sections", []):
				for column in section.get("columns", []):
					field_list = column.get("fields", [])
					for i, field in enumerate(field_list):
						if field == "annual_revenue":
							field_list[i] = "deal_value"

	allowed_fields = []
	for tab in tabs:
		for section in tab.get("sections"):
			if "columns" not in section:
				continue
			for column in section.get("columns"):
				if not column.get("fields"):
					continue
				allowed_fields.extend(column.get("fields"))

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldname in allowed_fields]

	required_fields = []

	if type == "Required Fields":
		required_fields = [
			field for field in frappe.get_meta(doctype, False).fields if field.reqd and not field.default
		]

	for tab in tabs:
		for section in tab.get("sections"):
			if section.get("columns"):
				section["columns"] = [column for column in section.get("columns") if column]
			for column in section.get("columns") if section.get("columns") else []:
				column["fields"] = [field for field in column.get("fields") if field]
				for field in column.get("fields") if column.get("fields") else []:
					field = next((f for f in fields if f.fieldname == field), None)
					if field:
						field = field.as_dict()
						handle_perm_level_restrictions(field, doctype, parent_doctype)
						column["fields"][column.get("fields").index(field["fieldname"])] = field

						# remove field from required_fields if it is already present
						if (
							type == "Required Fields"
							and field.reqd
							and any(f.get("fieldname") == field.get("fieldname") for f in required_fields)
						):
							required_fields = [
								f for f in required_fields if f.get("fieldname") != field.get("fieldname")
							]

	if type == "Required Fields" and required_fields and tabs:
		tabs[-1].get("sections").append(
			{
				"label": "Required Fields",
				"name": "required_fields_section_" + str(random_string(4)),
				"opened": True,
				"hideLabel": True,
				"columns": [
					{
						"name": "required_fields_column_" + str(random_string(4)),
						"fields": [field.as_dict() for field in required_fields],
					}
				],
			}
		)

	return tabs or []
