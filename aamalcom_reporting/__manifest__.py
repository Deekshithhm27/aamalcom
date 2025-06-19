
{
    'name': "Aamalcom Reporting",
    'summary': """Aamalcom Reporting """,
    'description': """
        Manage Reports in Visa Process .
    """,
    'author': 'Lucidspire.',
    'website': 'http://www.lucidspire.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr','visa_process'],
    'data': [
        'security/ir.model.access.csv',
        'views/reporting_menu.xml',
        'views/onboarding_report_wizard.xml',
        'reports/onboarding_report_template.xml',
        'reports/onboarding_report_action.xml',
        'views/muqeem_report_wizard.xml',
        'reports/muqeem_report_action.xml',
        'reports/muqeem_report_template.xml',
        'views/transfer_report_wizard.xml',
        'reports/transfer_report_action.xml',
        'reports/transfer_report_template.xml',
    ],
    'installable': True,
    'application': True,
}
