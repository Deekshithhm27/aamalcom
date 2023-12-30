# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class EmploymentDuration(models.Model):

    _name = 'employment.duration'
    _order = 'name asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Employment Duration"

    name = fields.Char(string="Duration",help="3 months, 6 months, 1 year etc..",tracking=True)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa')],string="Service Request Type",tracking=True)
    service_request_config_id = fields.Many2one('service.request.config',string="Service Request",domain="[('service_request_type','=',service_request_type)]")