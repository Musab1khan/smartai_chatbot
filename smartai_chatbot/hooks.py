app_name = "smartai_chatbot"
app_title = "smart_ai_chatbot"
app_publisher = "Umair Wali"
app_description = "chatbot"
app_email = "umairwali6@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "smartai_chatbot",
# 		"logo": "/assets/smartai_chatbot/logo.png",
# 		"title": "smart_ai_chatbot",
# 		"route": "/smartai_chatbot",
# 		"has_permission": "smartai_chatbot.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/smartai_chatbot/css/smartai_chatbot.css"
# app_include_js = "/assets/smartai_chatbot/js/smartai_chatbot.js"

# include js, css files in header of web template
# web_include_css = "/assets/smartai_chatbot/css/smartai_chatbot.css"
# web_include_js = "/assets/smartai_chatbot/js/smartai_chatbot.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "smartai_chatbot/public/scss/website"

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
# app_include_icons = "smartai_chatbot/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "smartai_chatbot.utils.jinja_methods",
# 	"filters": "smartai_chatbot.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "smartai_chatbot.install.before_install"
# after_install = "smartai_chatbot.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "smartai_chatbot.uninstall.before_uninstall"
# after_uninstall = "smartai_chatbot.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "smartai_chatbot.utils.before_app_install"
# after_app_install = "smartai_chatbot.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "smartai_chatbot.utils.before_app_uninstall"
# after_app_uninstall = "smartai_chatbot.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "smartai_chatbot.notifications.get_notification_config"

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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

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
# 		"smartai_chatbot.tasks.all"
# 	],
# 	"daily": [
# 		"smartai_chatbot.tasks.daily"
# 	],
# 	"hourly": [
# 		"smartai_chatbot.tasks.hourly"
# 	],
# 	"weekly": [
# 		"smartai_chatbot.tasks.weekly"
# 	],
# 	"monthly": [
# 		"smartai_chatbot.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "smartai_chatbot.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "smartai_chatbot.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "smartai_chatbot.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["smartai_chatbot.utils.before_request"]
# after_request = ["smartai_chatbot.utils.after_request"]

# Job Events
# ----------
# before_job = ["smartai_chatbot.utils.before_job"]
# after_job = ["smartai_chatbot.utils.after_job"]

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
# 	"smartai_chatbot.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Required apps
required_apps = ["frappe", "erpnext"]

# DocTypes
doctype_js = {
    "Chat Session": "public/js/chat_session.js",
    "AI API Configuration": "public/js/ai_config.js",
}

# Desktop icons
desktop_icons = [
    "SmartAI Chatbot"
]

# Setup wizard
setup_wizard_requires = ["smartai_chatbot"]

# Scheduled Jobs (Background Tasks)
scheduler_events = {
    "daily": [
        "smartai_chatbot.scheduler.send_daily_reports",
        "smartai_chatbot.scheduler.check_low_stock_alerts",
    ],
    "hourly": [
        "smartai_chatbot.scheduler.cleanup_old_sessions",
        "smartai_chatbot.scheduler.sync_ai_usage",
    ],
    "all": [
        "smartai_chatbot.scheduler.process_autonomous_actions",
    ]
}

# Custom DocTypes
fixtures = [
    {"dt": "DocType", "name": "AI API Configuration"},
    {"dt": "DocType", "name": "Chat Session"},
    {"dt": "DocType", "name": "Chat Message"},
    {"dt": "DocType", "name": "AI Report"},
    {"dt": "DocType", "name": "Autonomous Action"},
    {"dt": "DocType", "name": "AI Usage Log"},
    {"dt": "DocType", "name": "AI Training Data"},
]

# Permissions
has_permission = {
    "Chat Session": "smartai_chatbot.permissions.has_chat_session_permission",
}

# API endpoints
api_endpoints = {
    "smartai_chatbot": "smartai_chatbot.api",
}

# Translation
translate_docs = ["Chat Session", "AI API Configuration"]

# Hide modules that shouldn't appear in sidebar
hide_in_desk = []

# App initialization
app_include_js = [
    "assets/smartai_chatbot/js/bundle.min.js",
]

app_include_css = [
    "assets/smartai_chatbot/css/style.css",
]

# Whitelisted methods
whitelist = [
    "smartai_chatbot.api.ai_gateway.chat",
    "smartai_chatbot.api.ai_gateway.create_session",
    "smartai_chatbot.api.ai_gateway.get_recent_chats",
    "smartai_chatbot.api.data_processor.get_erp_data",
    "smartai_chatbot.api.chart_generator.generate_chart",
    "smartai_chatbot.api.export_manager.export_report",
    "smartai_chatbot.api.autonomous_agent.execute_action",
    "smartai_chatbot.api.voice_handler.process_audio",
]

# On document save/update
doc_events = {
    "AI API Configuration": {
        "after_insert": "smartai_chatbot.events.ai_config_after_insert",
        "on_update": "smartai_chatbot.events.ai_config_on_update",
    },
    "Chat Session": {
        "before_save": "smartai_chatbot.events.chat_session_before_save",
        "after_delete": "smartai_chatbot.events.chat_session_after_delete",
    }
}

# Standard ports
standard_portal_menu_items = [
    {"title": "SmartAI Chatbot", "route": "/app/smartai-chat", "reference_doctype": "Chat Session"},
]

# Extend existing doctypes
standard_queries_for_doctypes = {
    "Chat Session": "smartai_chatbot.queries.get_chat_sessions",
}

app_include_js = ["smartai_chatbot/js/chat_button.js"]
