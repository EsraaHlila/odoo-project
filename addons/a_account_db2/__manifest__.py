{
    'name': 'Invoice Unique Company',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Replace invoice partner with Unique Company',
    'author': 'Your Name',
    'depends': ['account'],  # Replace with your actual module name
    'data': [
        'views/account_move_form.xml',
        'views/report_invoice_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
