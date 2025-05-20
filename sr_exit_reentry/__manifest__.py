# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Exit Rentry Service',
    'version': '1.0',
    'summary': 'Module for managing Exit Rentry Service requests.',
    'description':"""
        This module allows client spoc to create, track, and manage Exit Rentry Service requests.
    """,
    'category': 'Services',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
        'depends': [
        'base',
        'mail',
        'visa_process','aamalcom_service_request'
    ],
    'data': [
        'views/service_enquiry_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}


