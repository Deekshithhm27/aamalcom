# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Muqeem Dropout',
    'version': '1.0',
    'summary': 'Module for managing Muqeem Dropout service requests.',
    'description':"""
        This module allows client spoc to create, track, and manage Muqeem Dropout service requests.
    """,
    'category': 'Services',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
    'depends': ['base', 'mail', 'visa_process','sr_iqama_requests'],
    'data': [
        'views/service_enquiry_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}


