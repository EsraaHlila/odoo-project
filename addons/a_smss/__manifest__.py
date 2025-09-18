{
    'name': "TextBee SMS Integration",
    'summary': "Send SMS via TextBee API",
    'description': "Send SMS messages using the TextBee API gateway",
    'author': "Your Name",
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/sms_composer_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}