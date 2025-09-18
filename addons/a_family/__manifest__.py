{
    'name': 'Family Management',
    'version': '1.0.0',
    'summary': 'Manage Parents and Children',
    'description': 'Handles parent-child relationships',
    'author': 'Your Company',
    'depends': ['base', 'crm'],
    'data': [
        # Data files
        'data/unique_parent_sequence.xml',
        'data/unique_child_sequence.xml',
        
        # Views
        'views/parent_views.xml',
        'views/child_views.xml',
        
        # Menus
        'views/parent_menu.xml',
        'views/child_menu.xml',
        
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}