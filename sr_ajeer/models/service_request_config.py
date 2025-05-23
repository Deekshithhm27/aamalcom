from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('ajeer_permit', 'Ajeer Permit')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'ajeer_permit': 'cascade'}

    )