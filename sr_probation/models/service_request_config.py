from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('probation_request', 'Extend Probation')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'probation_request': 'cascade'}

    )