# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResUsers(models.Model):
    _inherit = "res.users"

    user_type = fields.Selection([('external','External'),('internal','Internal')],string="Type of user to set System Access",required=True)
    internal_company_id = fields.Many2one('res.company',string="Company")
    partner_company_id = fields.Many2one('res.partner',string="Company",domain="[('is_company','=',True)]")

    company_spoc_id = fields.Many2one('hr.employee',string="Project Manager",domain="[('custom_employee_type','=','internal')]")


    def action_create_employee(self):
        self.ensure_one()
        self.env['hr.employee'].create(dict(
            name=self.name,
            company_id=self.env.company.id,
            **self.env['hr.employee']._sync_user(self)
        ))

    @api.onchange('internal_company_id')
    def update_user_company_id(self):
        # this method is used to update the parent_id of internal user
        # parent_company_id is the value which is being fetched in res.partner which depends on user_ids
        # so in this method, we are directly updating the internal user's company to parent_company_id
        for line in self:
            line.partner_company_id = line.internal_company_id.partner_id.id

    @api.onchange('user_type')
    def reset_company_id(self):
        for line in self:
            if line.user_type == 'external':
                line.internal_company_id = False