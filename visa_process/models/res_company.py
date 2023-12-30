# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil import relativedelta as rdelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResCompany(models.Model):
    _inherit = 'res.company'

    vat = fields.Char(related='partner_id.vat', string="VAT ID", readonly=False)