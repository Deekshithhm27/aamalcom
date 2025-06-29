# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Salary Increase Process',
    'version': '1.0',
    'summary': 'Management of Salary Increase New Service Request',
    'description': """
Aamalcom Service Request
============================
This module provides a centralized platform to manage and configure service request of type letters in the Odoo system. 

""",
    'category': 'Visa Process',
    'author': 'Lucidspire',
    'website': 'http://www.lucidspire.com',
    'depends': ['base', 'mail', 'visa_process','account','aamalcom_payroll'],
    'data': [
    'security/ir.model.access.csv',
    'views/service_enquiry_views.xml', 
    'views/emp_salary_views.xml'  
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}


