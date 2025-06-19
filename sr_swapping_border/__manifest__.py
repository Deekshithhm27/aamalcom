# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Swapping from Border to Iqama NUmber service request',
    'version': '1.0',
    'summary': 'Management of Phase 2  Service Request',
    'description': """
Aamalcom Service Request
============================
This module provides a centralized platform to manage and configure new service request in the Odoo system. 

""",
    'category': 'Visa Process',
    'author': 'Aamalcom',
    'website': 'http://www.aamalcom.com',
    'depends': ['base','visa_process','account','hr'],
    'data': [
        'views/service_enquiry_views.xml',  
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}


