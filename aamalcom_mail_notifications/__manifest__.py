# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Aamalcom Mail Notifications',
    'version': '1.0',
    'summary': 'Centralized management of commonly sent mail notifications.',
    'description': """
Aamalcom Mail Notifications
============================
This module provides a centralized platform to manage and configure commonly sent mail notifications in the Odoo system. 
It allows for streamlined and automated email communications for various use cases.
""",
    'category': 'Tools',
    'author': 'Aamalcom',
    'website': 'http://www.aamalcom.com',
    'depends': ['base', 'mail', 'visa_process'],
    'data': [
        'security/ir.model.access.csv',
        'views/service_enquiry_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}


