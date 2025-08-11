# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ServiceRequestConfg(models.Model):
    _name = "service.request.config"
    _order = 'sequence asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string="Service",compute='update_name',store=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean('Active', default=True)

    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa'),('twv_request','Temporary Work Visa')],string="Service Request Type",default='lt_request',tracking=True)

    service_request = fields.Selection([('new_ev','Issuance of New EV'),
        ('hr_card','Issuance for HR card'),('transfer_req','Transfer Request Initiation'),
        ('ins_class_upgrade','Medical health insurance Class Upgrade'),
        ('iqama_no_generation','Iqama No generation'),('iqama_card_req','New Physical Iqama Card Request'),
        ('qiwa','Qiwa Contract'),('gosi','GOSI Update'),('iqama_renewal','Iqama Renewal'),
        ('prof_change_qiwa','Profession change Request In qiwa'),
        ('final_exit_issuance','Final exit Issuance'),
        ('dependent_transfer_query','Dependent Transfer Query'),('soa','Statement of account till date')],string="Requests",required=True)

    sequence = fields.Integer(string="Sequence",help="Gives the sequence order when displaying a list of Service Types in Tickets.")

    service_department_lines = fields.One2many('service.department.line','service_req_id',string="Department Lines")

    process_type = fields.Selection([('automatic','Automatic'),('manual','Manual')],string="Process Type")
    
    _sql_constraints = [
        ('name_service_request_type_uniq', 'unique (name,service_request_type)', 'The Service type is already defined !')
    ]

    @api.depends('service_request_type', 'service_request')
    def update_name(self):
        for line in self:
            service_request_type = dict(self._fields['service_request_type'].selection).get(line.service_request_type)
            service_request = dict(self._fields['service_request'].selection).get(line.service_request)
            if line.service_request_type == 'ev_request':
                line.name = ''.join([ service_request or ''])
            else:
                line.name = ''.join([service_request or ''])

class ServiceDepartmentLine(models.Model):
    _name = 'service.department.line'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    service_req_id = fields.Many2one('service.request.config',string="Request id")
    name = fields.Char(string="Service Request",compute='update_name',store=True)

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    department_id = fields.Many2one('hr.department',string="Department")
    sequence = fields.Integer(string="Sequence",default="1")


    @api.depends('service_req_id', 'department_id')
    # modify this later
    def update_name(self):
        for line in self:
            if line.service_req_id:
                service_req_id = line.service_req_id.name
                department_id = line.department_id.name
                if line.service_req_id:
                    line.name = ''.join([ service_req_id,' - ',department_id or ''])
                else:
                    line.name = ''.join([department_id or ''])


