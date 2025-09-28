{
    'name': 'Aamalcom Access Control',
    'version': '15.0.1.0.0',
    'summary': 'Dynamic Menu Access Control by Levels',
    'category': 'Accounting/Finance',
    'author': 'Your Name',
    'depends': ['base', 'hr','account','visa_process'],
    'data': [
        'security/ir.model.access.csv',
        'views/finance_access_level_views.xml',
        'views/menu_access_history_views.xml',
        'wizard/finance_access_wizard_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}
