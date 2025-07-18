from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('health_insurance', 'Health Insurance -Enrollment on Border Number'),
            ('enrollment_for_work_visa', 'Enrollment for Work Visit Visa')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'health_insurance': 'cascade','enrollment_for_work_visa':'cascade'}
    )