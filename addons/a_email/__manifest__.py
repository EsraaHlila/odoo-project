{
    'name': 'Email Integration',
    'version': '1.0',
    'summary': 'Send Emails',
    'category': 'Tools',
    'depends': ['base', 'web','a_company'],
    'data': [
        'data/sequence.xml',
        'views/email_send_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}