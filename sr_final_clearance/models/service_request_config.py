from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('final_clearance', 'Final Clearance')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'final_clearance': 'cascade'}
    )