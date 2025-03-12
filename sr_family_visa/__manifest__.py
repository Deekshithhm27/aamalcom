# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Aamalcom Family Resident application',
    'version': '1.0',
    'summary': 'Management of Family Resident application',
    'description': """
Aamalcom Service Request
============================
This module provides a centralized platform to manage and configure service request of type Family Resident Application  in the Odoo system. 

""",
    'category': 'Tools',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
    'depends': ['base', 'mail', 'visa_process'],
    'data': [
    'views/service_enquiry_views.xml',      
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}


