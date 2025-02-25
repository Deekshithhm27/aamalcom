# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class ServiceRequestConfg(models.Model):
    _inherit = "service.request.config"

    service_request = fields.Selection(selection_add=[('muqeem_dropout', 'Muqeem  Dropout')],ondelete={'muqeem_dropout': 'cascade'})

