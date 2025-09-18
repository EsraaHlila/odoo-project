{
    'name': 'Subscription Manager',
    'version': '1.0.0',
    'summary': 'Completely unique subscription management',
    'description': 'Handles all subscription operations',
    'author': 'Your Company',
    'category': 'Sales/Special',
    'depends': ['base','sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/subscription_menu.xml',
        'views/subscription_views.xml',
        'views/action.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': '_init_sequence_hook',  # This is the new line
}