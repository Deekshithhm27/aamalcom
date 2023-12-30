# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class SalaryStructure(models.Model):
    _name = 'hr.client.salary.rule'
    _order = 'sequence asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Salary Structure"

    name = fields.Char(string="Type",tracking=True)
    code = fields.Char(string="Code",tracking=True)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    sequence = fields.Integer(string="Sequence")


class SalaryLines(models.Model):
    _name = "salary.line"
    _order = 'sequence asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Many2one('hr.client.salary.rule',string="Structure Type")
    sequence = fields.Integer(string="Sequence",related="name.sequence",store=True)

    emp_visa_id = fields.Many2one('employment.visa',string="Employment Visa Id")
    ev_enq_visa_id = fields.Many2one('service.enquiry',string="EV Service Enquiry")
    local_transfer_id = fields.Many2one('local.transfer',string="Local Transfer Id")
    
    amount = fields.Float(string="Amount")
