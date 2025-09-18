{
    'name': 'CRM Customizations',
    'version': '1.0.0',  # Recommended version format
    'summary': 'Custom CRM modifications',  # Add short description
    'category': 'CRM',
    'sequence': 10,  # Display order in category
    'author': 'Your Name',  # Add author
    'website': 'https://yourwebsite.com',  # Add website if available
    'depends': [
        'base',
        'sale',
        'crm'  # Explicitly add if using CRM features
    ],
    'data': [ # Alphabetical order
        'views/res_partner_views.xml',
    ],
    'demo': [],  # Explicit empty demo data
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',  # Specify license
}