from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('iqama_correction', 'Iqama Correction')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'iqama_correction': 'cascade'}
    )