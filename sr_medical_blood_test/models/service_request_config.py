from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
        selection_add=[
            ('medical_blood_test', 'Iqama Issuance-Medical Blood Test')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'medical_blood_test': 'cascade'}

    )