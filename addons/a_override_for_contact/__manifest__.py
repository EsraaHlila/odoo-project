{
    'name': 'Default Company Type to Person',
    'version': '1.0',
    'summary': 'Sets default company_type to "person" in partner form',
    'description': """
        Forces the company_type radio button to default to "Person" (individual) instead of "Company".
    """,
    'author': 'esraa',
    'category': 'Contacts',
    'depends': ['base'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}