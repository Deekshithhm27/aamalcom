from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('bank_loan','Bank Loan Letter')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'bank_loan': 'cascade'}

    )