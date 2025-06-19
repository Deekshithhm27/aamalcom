{
    'name': 'Aamalcom Insurance',
    'version': '15.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage employee reimbursements with automatic credit note creation',
    'depends': ['base', 'account', 'hr','visa_process'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/account_move_views.xml',
        'views/insurance_reimbursement_view.xml',
        'views/medical_insurance_deletion_views.xml',
        'views/life_insurance_deletion_views.xml',

        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
