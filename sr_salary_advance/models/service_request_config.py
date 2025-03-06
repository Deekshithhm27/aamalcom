from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('salary_advance', 'Salary Advance')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'salary_advance': 'cascade'}

    )