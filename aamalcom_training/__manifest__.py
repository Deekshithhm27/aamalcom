
{
    'name': 'Aamalcom Training',
    'version': '1.0',
    'summary': 'Custom Training announcement for internal users',
    'category': 'Human Resources',
    'author': 'Grok Assistant',
    'depends': ['hr_holidays', 'hr', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/training_course_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}