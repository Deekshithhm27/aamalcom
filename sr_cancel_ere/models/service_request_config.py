from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('cancel_ere','Cancel Exit Rentry issuance')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'cancel_ere': 'cascade'}
    )