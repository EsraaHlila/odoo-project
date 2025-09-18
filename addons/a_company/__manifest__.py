{
    'name': 'company Processor',
    'version': '1.0.0',
    'summary': 'Completely unique company processing',
    'description': 'Handles company',
    'author': 'Your Company',
    'depends': ['base','crm'],
    'data': [
        'data/unique_company_sequence.xml',
        'views/company_views.xml',
        'views/company_menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}