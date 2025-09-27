# -*- coding: utf-8 -*-

{
    'name': 'Odoo 15 Accounting Financial Reports in XSLX',
    'version': '15.0.8.2.0',
    'category': 'Invoicing Management',
    'description': 'Accounting Reports For Odoo 15, Accounting Financial Reports, '
                   'Odoo 15 Financial Reports',
    'summary': 'Accounting Reports For Odoo 15',
    'sequence': '1',
    'author': 'Odoo Mates, Odoo SA',
    'license': 'LGPL-3',
    'company': 'Odoo Mates',
    'maintainer': 'Odoo Mates',
    'support': 'odoomates@gmail.com',
    'website': 'https://www.youtube.com/watch?v=yA4NLwOLZms',
    'depends': ['base',
    'account',
    'report_xlsx',
    'accounting_pdf_reports',],
    'live_test_url': 'https://www.youtube.com/watch?v=yA4NLwOLZms',
    'data': [
        'views/profit_and_loss.xml',
        'views/gneral_ledger_views.xml', # This defines the wizard's form view with the XLSX button
        'report/general_ledger.xml', # ✅ ADD THIS LINE - This defines the ir.actions.report
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}