{
    'name': 'Account Droit de Timbre',
    #'version': '16.0.1.0.0',  # or 18.0 if you're on Odoo 18
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
        'views/report_invoice_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
