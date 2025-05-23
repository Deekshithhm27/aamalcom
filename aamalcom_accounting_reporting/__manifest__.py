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
    'depends': ['account', 'accounting_pdf_reports'],
    'data': [
        'report/report_journal_entries.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
