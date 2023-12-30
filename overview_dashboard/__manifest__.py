# -*- coding: utf-8 -*-

{
    'name': 'Dashboard for Approvals',
    'version': '15.0.1.0.1',
    "category": "Generic Modules/Human Resources",
    'summary': 'Customisations for Employee module',
    'description': 'Customisations for Employee module',
    'author': 'Lucidspire',
    'company': 'Lucidspire',
    'maintainer': 'Lucidspire',
    'website': 'https://www.lucidspire.com',
    'depends': ['hr','base','visa_process'],
    'data': [
    		'security/ir_rule.xml',
             'views/hr_employee_views.xml',
             'views/service_enquiry_views.xml',
             'views/hr_employee_overview.xml'
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
