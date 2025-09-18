{
    'name': 'package Processor',
    'version': '1.0.0',
    'summary': 'Completely unique package processing',
    'description': 'Handles package',
    'author': 'Your Company',
    'depends': ['base','crm'],
    'data': [
        'data/unique_package_sequence.xml',
        'views/package_views.xml',
        'views/package_menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}