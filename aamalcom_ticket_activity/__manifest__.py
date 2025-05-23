# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Aamalcom Ticket Activity',
    'version': '1.0',
    'license': 'OPL-1',
    'summary': 'Manage ticket flows with activities assigned to specific handlers',
    'sequence': 10,
    'author': 'Aamalcom',
    'website': 'https://www.aamalcom.com',
    'category': 'Operations/Workflow',
    'depends': ['base', 'mail', 'visa_process','sr_iqama_requests','sr_exit_reentry', 'sr_muqeem'],
    'data': [
        'data/activity.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

