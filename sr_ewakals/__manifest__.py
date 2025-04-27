# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'E-Wakala Service Request',
    'version': '1.0',
    'summary': 'Management of all  Service Request E-Wakala',
    'description': """
Aamalcom Service Request
============================
This module provides a centralized platform to manage and configure service request of type letters in the Odoo system. 

""",
    'category': 'Tools',
    'author': 'Aamalcom',
    'website': 'http://www.aamalcom.com',
    'depends': ['base','visa_process','account'],
    'data': [
    'views/service_enquiry_views.xml',      
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}


