{
    'name': 'Probation Serice Request',
    'version': '1.0.0',
    'summary': 'Manage client employee info change requests with Service Request approval and notifications',
    'category': 'Operations',
    'author': 'Lucidspire',
    'website': 'https://lucidspire.com',
    'depends': ['hr', 'mail','visa_process', 'aamalcom_hr_operations'],
    'data': [
    'data/mail_template.xml',
    'data/ir_cron_probation.xml', 
    'views/service_enquiry_views.xml',
        
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}