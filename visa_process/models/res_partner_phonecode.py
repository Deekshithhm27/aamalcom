# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil import relativedelta as rdelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResPartnerPhonecode(models.Model):
    _name = 'res.partner.phonecode'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Phone Codes"

    name = fields.Char(string="Code")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    country_id = fields.Many2one('res.country',string='Country')

    def name_get(self):
        """ Display 'Warehouse_name: PickingType_name' """
        res = []
        for line in self:
            if line.country_id:
                name = line.name + ' (' + line.country_id.name + ')'
            else:
                name = line.name
            res.append((line.id, name))
        return res