# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ServiceRequestTreasury(models.Model):
    _name = 'service.request.treasury'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Reference Documents"

    name = fields.Char(string="Sequence",tracking=True)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")

    service_request_id = fields.Many2one('service.enquiry',string="Service Request")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client")
    employment_duration = fields.Many2one('employment.duration',string="Duration",tracking=True)
    total_amount = fields.Monetary(string="Price")

    state = fields.Selection([('draft','Draft'),('submitted','Submitted to Treasury'),('done','Done')],string="Status",default='draft')

    confirmation_doc = fields.Binary(string="Confirmation Doc")

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('service.request.treasury')
        res = super(ServiceRequestTreasury,self).create(vals_list)
        return res

    def action_submit(self):
        for line in self:
            line.state = 'submitted'

    def action_upload_confirmation(self):
        for line in self:
            line.state = 'done'