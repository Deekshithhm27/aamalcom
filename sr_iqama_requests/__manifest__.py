# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Iqama Requests Service',
    'version': '1.0',
    'summary': 'Module for managing iqama-related service requests.',
    'description':"""
        This module allows client spoc to create, track, and manage iqama-related service requests.
    """,
    'category': 'Services',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
    'depends': ['base', 'mail', 'visa_process','aamalcom_accounting',],
    'data': [
        'views/service_enquiry_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}


