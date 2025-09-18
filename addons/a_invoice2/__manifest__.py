{
    "name": "DMNova Custom Invoice Report",
    "version": "1.0.0",
    "summary": "Custom invoice (Facture) PDF layout for customer invoices",
    "description": "Provides a custom QWeb PDF invoice template (Facture) for account.move (customer invoices).",
    "author": "You / DMNova",
    "category": "Accounting",
    "depends": ["account", "web"],
    "data": [
        "views/report_invoice_templates.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
