# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class VisaRefDocument(models.Model):
    _name = 'visa.ref.documents'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Reference Documents"

    name = fields.Char(string="Document Name",tracking=True)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    is_medical_doc = fields.Boolean(string="Is Medical Doc")
    medical_doc = fields.Binary(string="File")

    is_istiqdam_doc = fields.Boolean(string="Is Istiqdam Doc")
    istiqdam_doc = fields.Binary(string="File")

