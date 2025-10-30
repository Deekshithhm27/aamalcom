from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('iqama_correction', 'Correction of Personal Information - (Iqama/Muqeem)')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'iqama_correction': 'cascade'}
    )