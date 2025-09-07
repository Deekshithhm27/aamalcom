# aamalcom_time_off/__manifest__.py
{
    'name': 'Aamalcom Time Off',
    'version': '1.0',
    'summary': 'Custom leave types with multi-level approvals and validations',
    'category': 'Human Resources',
    'author': 'Grok Assistant',
    'depends': ['hr_holidays', 'hr', 'mail','visa_process','hr_work_entry_contract','hr_work_entry_holidays'],
    'data': [
        # 'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_leave_type_data.xml',
        'data/mail_templates.xml',
        'views/hr_leave_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
}