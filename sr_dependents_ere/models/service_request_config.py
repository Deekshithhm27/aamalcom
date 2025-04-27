from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('dependents_ere', 'Dependents ExitRentry')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'dependents_ere': 'cascade'}
    )