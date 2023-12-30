# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Aamalcom Accouting",
    'summary': """Accounting Integration""",
    'description': """
        Integration with Operations and Accounting
    """,
    'author': 'Lucidspire.',
    'website': 'http://www.lucidspire.com',
    'category': 'Generic Modules/Accounting',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['base','visa_process','account','om_account_followup','om_recurring_payments','payment','om_account_budget','utm'],
    'data': [
    	'security/security.xml',
        'security/ir.model.access.csv',
    	'data/sequences.xml',
        'views/draft_account_move_views.xml',
        'views/account_payment_approval_views.xml',
        'views/account_payment_views.xml',
        'views/service_enquiry_views.xml',
        'views/account_move_views.xml',
        'wizard/batch_invoice_creation_wizard_views.xml',
        'views/menu_hide_views.xml',
        'views/menu.xml'

    ],
    'demo': [
        # 'demo/visa_demo.xml',
    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
