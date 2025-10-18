# -*- coding: utf-8 -*-

{
    'name': 'Aamalcom Accounting Financial Reports',
    'version': '1.0',
    'description': 'Aamalcom Accounting Financial Reports',
    'summary': 'Accounting Reports For Odoo 15',
    'license': 'OPL-1',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
    'category': 'Accounting',
    'depends': ['account','aamalcom_accounting','aamalcom_insurance','visa_process'],
    'data': [
        'reports/paperformat.xml',
        'reports/report_templates.xml',
        'reports/report_insurance_invoice.xml',
        'reports/report_invoice.xml',
        'reports/report_action.xml',
        'reports/report_journal_entries.xml',
        'data/mail_templates.xml',
        'views/account_move_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
