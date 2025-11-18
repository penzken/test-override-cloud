from crm.fcrm.doctype.crm_deal.crm_deal import CRMDeal

class CustomCRMDeal(CRMDeal):
	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Deal Value",
				"type": "Currency",
				"key": "deal_value",
				"align": "right",
				"width": "15rem",
			},
			{
			"label": "Status",
			"type": "Select",
			"key": "status",
			"width": "10rem",
		},
		{
			"label": "Email",
			"type": "Data",
			"key": "email",
			"width": "12rem",
		},
		{
			"label": "Mobile No",
			"type": "Data",
			"key": "mobile_no",
			"width": "11rem",
		},
		{
			"label": "Assigned To",
			"type": "Text",
			"key": "_assign",
			"width": "10rem",
		},
		{
			"label": "Last Modified",
			"type": "Datetime",
			"key": "modified",
			"width": "8rem",
		},
	]
		rows = [
		"name",
		"organization",
		"annual_revenue",
		"status",
		"email",
		"currency",
		"mobile_no",
		"deal_owner",
		"sla_status",
		"response_by",
		"first_response_time",
		"first_responded_on",
		"modified",
		"_assign",
	]
		return {"columns": columns, "rows": rows}