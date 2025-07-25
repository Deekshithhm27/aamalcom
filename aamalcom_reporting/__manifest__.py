
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
        'data/muqeem_email_template.xml',
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
        'reports/new_ev_action.xml',
        'reports/new_ev_template.xml',
        'views/new_ev_reports.xml',
        'reports/qiwa_action.xml',
        'reports/qiwa_template.xml',
        'views/qiwa_wizard.xml',
        'reports/final_action.xml',
        'reports/final_clearance_template.xml',
        'views/final_cleraance_views.xml'
    ],
    'installable': True,
    'application': True,
}
