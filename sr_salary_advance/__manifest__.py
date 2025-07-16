# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Aamalcom Salary Advance',
    'version': '1.0',
    'summary': 'Management of all  Service Request letters',
    'description': """
Aamalcom Service Request
============================
This module provides a centralized platform to manage and configure service request of type letters in the Odoo system. 

""",
    'category': 'Tools',
    'author': 'Aamalcom',
    'website': 'http://www.aamalcom.com',
    'depends': ['base', 'mail', 'visa_process','aamalcom_accounting','account','l10n_gcc_invoice','om_account_followup','om_recurring_payments','payment','om_account_budget','utm'],
    'data': [
    'views/service_enquiry_views.xml', 
    'views/service_request_treasury_views.xml',
    'views/draft_acoount_move_views.xml' 
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}


