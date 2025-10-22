from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('visa_cancellation', 'Work Visa Cancellation')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'visa_cancellation': 'cascade'}

    )