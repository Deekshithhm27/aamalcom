{
    'name': 'Aamalcom  Internal Treasury ',
    'version': '15.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Internal Treasury',
    'depends': ['base', 'account', 'hr','visa_process','aamalcom_hr_operations'],
    'data': [
    'security/ir.model.access.csv',
    'data/ir.sequence.xml',
    'views/internal_views.xml',
    'views/menu.xml'
        
    ],
    'installable': True,
    'application': True,

}
