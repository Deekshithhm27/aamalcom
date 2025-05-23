from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('visitor_report', 'Visitor Report')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'visitor_report': 'cascade'}

    )