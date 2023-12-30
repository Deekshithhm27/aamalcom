# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Aamalcom Payroll",
    'summary': """Customised Payroll for Aamalcom""",
    'description': """
        Customised Payroll for Aamalcom
    """,
    'author': 'Lucidspire.',
    'website': 'http://www.lucidspire.com',
    'category': 'Generic Modules/Accounting',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['base','visa_process','hr','om_hr_payroll','mail','account','contacts','hr_holidays'],
    'data': [
    	'data/sequences.xml',
    	'data/client_salary_rules.xml',
    	'data/hr_payroll_data.xml',
    	'security/ir.model.access.csv',
        'views/gosi_charges_views.xml',
        'views/hr_contract_views.xml',
    	'views/salary_structure_views.xml',
    	'views/employment_visa_views.xml',
    	'views/local_transfer_views.xml',
    	'views/hr_salary_rule_views.xml',
    	'views/hr_employee_views.xml',
    	'views/client_employee_monthly_salary_tracking_views.xml',
        'views/hr_payslip_views.xml',
    	'views/hr_payslip_employees_views.xml',
        'views/account_move_views.xml',
        'wizard/client_emp_salary_tracking_wizard.xml',
    	'views/menu_views.xml'

    	

    ],
    'demo': [
        # 'demo/visa_demo.xml',
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
