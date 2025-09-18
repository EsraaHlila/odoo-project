{
    "name": "DM CRM Automation",
    "version": "1.0.0",
    "summary": "Welcome emails, inactivity reminders, and campaign broadcasts",
    "category": "CRM",
    "author": "You",
    "depends": ["crm", "mail", "marketing_automation"],  # remove "marketing_automation" if not used
    "data": [
        "data/mail_templates.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
