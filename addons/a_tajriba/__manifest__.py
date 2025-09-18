{
    'name': 'Subscription Management',
    'version': '1.0',
    'summary': 'Manage subscriptions and payments',
    'description': """
        This module allows you to manage customer subscriptions and related payments.
        It includes features for tracking parent/child information and processing payments.
    """,
    'author': 'esraa',
    'category': 'Sales',
    'depends': ['base'],
    'data': [
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}