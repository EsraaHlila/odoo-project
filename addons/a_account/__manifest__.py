{
    'name': 'Invoice Unique Company',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Replace invoice partner with Unique Company',
    'author': 'Your Name',
    'depends': ['account', 'a_company'],  # Replace with your actual module name
    'data': [
        'views/account_move_form.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
