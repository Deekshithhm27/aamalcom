# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Aamalcom Accounting Approvals',
    'version': '1.0',
    'license': 'OPL-1',
    'summary': 'Approval workflow',
    'description': '''
        This module adds an approval workflow .
    ''',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
    'category': 'Accounting',
    'depends': ['account', 'aamalcom_accounting','visa_process'],
    'data': [
        'data/sequences.xml',
        'security/security.xml',
        'views/account_move_views.xml',
        'views/account_payment_approval_views.xml',
        'views/account_payment_views.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'application': False,
}
