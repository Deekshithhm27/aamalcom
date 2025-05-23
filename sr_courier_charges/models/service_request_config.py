from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('courier_charges', 'Courier')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'courier_charges': 'cascade'}
    )