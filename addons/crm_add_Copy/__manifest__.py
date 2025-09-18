{
    'name': 'CRM Customizations',
    'version': '1.0',
    'category': 'CRM',
    'depends': ['base', 'sale'],
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}