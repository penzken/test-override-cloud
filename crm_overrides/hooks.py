app_name = "crm_overrides"
app_title = "Crm Overrides"
app_publisher = "Thang"
app_description = "Overried CRM"
app_email = "lethang507@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "crm_overrides",
# 		"logo": "/assets/crm_overrides/logo.png",
# 		"title": "Crm Overrides",
# 		"route": "/crm_overrides",
# 		"has_permission": "crm_overrides.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/crm_overrides/css/crm_overrides.css"
# app_include_js = "/assets/crm_overrides/js/crm_overrides.js"

# include js, css files in header of web template
# web_include_css = "/assets/crm_overrides/css/crm_overrides.css"
# web_include_js = "/assets/crm_overrides/js/crm_overrides.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "crm_overrides/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "crm_overrides/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "crm_overrides.utils.jinja_methods",
# 	"filters": "crm_overrides.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "crm_overrides.install.before_install"
# after_install = "crm_overrides.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "crm_overrides.uninstall.before_uninstall"
# after_uninstall = "crm_overrides.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "crm_overrides.utils.before_app_install"
# after_app_install = "crm_overrides.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "crm_overrides.utils.before_app_uninstall"
# after_app_uninstall = "crm_overrides.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "crm_overrides.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"CRM Lead": "crm_overrides.overrides.crm_lead.CustomCRMLead",
	"CRM Deal": "crm_overrides.overrides.crm_deal.CustomCRMDeal",
}

override_whitelisted_methods = {
	"crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout": "crm_overrides.overrides.fields_layout.get_fields_layout",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"crm_overrides.tasks.all"
# 	],
# 	"daily": [
# 		"crm_overrides.tasks.daily"
# 	],
# 	"hourly": [
# 		"crm_overrides.tasks.hourly"
# 	],
# 	"weekly": [
# 		"crm_overrides.tasks.weekly"
# 	],
# 	"monthly": [
# 		"crm_overrides.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "crm_overrides.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "crm_overrides.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "crm_overrides.event.get_events"
# }

# Website Route Rules
# --------------------
website_route_rules = [
	{"from_route": "/crm/<path:app_path>", "to_route": "crm"},
]
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "crm_overrides.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["crm_overrides.utils.before_request"]
# after_request = ["crm_overrides.utils.after_request"]

# Job Events
# ----------
# before_job = ["crm_overrides.utils.before_job"]
# after_job = ["crm_overrides.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"crm_overrides.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

