{
    'name': 'TextBee SMS Integration',
    'version': '1.0',
    'summary': 'Send SMS via TextBee API',
    'category': 'Tools',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web','a_family'],
    'data': [
        'data/sequence.xml',
        'views/res_config_settings_views.xml',
        'views/sms_textbee_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}