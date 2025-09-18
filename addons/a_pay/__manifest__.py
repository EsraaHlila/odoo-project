{
    'name': 'Payment Processor',
    'version': '1.0.0',
    'summary': 'Completely unique payment processing',
    'description': 'Handles all payment operations',
    'author': 'Your Company',
    'category': 'Finance/Special',
    'depends': ['base','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_menu.xml',
        'data/payment_sequence.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}