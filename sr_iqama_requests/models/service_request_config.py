from odoo import models, fields, api, _


class ServiceRequestConfig(models.Model):
    _inherit = "service.request.config"

    service_request = fields.Selection(
        selection_add=[('iqama_print', 'Iqama Print')], string="Requests", required=True,ondelete={'iqama_print': 'cascade'})