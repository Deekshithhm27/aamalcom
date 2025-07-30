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
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Reference Documents"

    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa'),('twv_request','Temporary Work Visa')],string="Service Request Type",tracking=True,copy=False)
    service_request_config_id = fields.Many2one('service.request.config',string="Service Request",domain="[('service_request_type','=',service_request_type)]",copy=False)
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
    issue_date = fields.Date(string='Issue Date')

    state = fields.Selection([('draft','Draft'),('updated_by_treasury','Waiting for Approval'),('passed_to_treasury','Passed to Treasury'),('submitted','Submitted to Treasury'),('done','Done')],string="Status",default='draft',tracking=True)

    confirmation_doc = fields.Binary(string="Confirmation Doc*")
    confirmation_doc_ref = fields.Char(string="Ref No.*")
    bank_receipt_one = fields.Binary(string="1. Bank Receipt")
    bank_receipt_two = fields.Binary(string="2. Bank Receipt")
    bank_receipt_three = fields.Binary(string="3. Bank Receipt")
    other_doc = fields.Binary(string="Others")

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('service.request.treasury')
        res = super(ServiceRequestTreasury,self).create(vals_list)
        return res

    def action_submit(self):
        for line in self:
            line.state = 'submitted'
            line.service_request_id.dynamic_action_status = f'Submitted to the Treasury Department by FM. Document upload confirmation is pending.'

    def action_upload_confirmation(self):
        for line in self:
            if line.confirmation_doc and not line.confirmation_doc_ref:
                raise ValidationError("Kindly Update Reference Number for Confirmation  Document")
            if not line.issue_date:
                raise ValidationError("Kindly update issue date before upload confirmation")
            # Upload documents for specific services
            if line.service_request_id.service_request in ['new_ev', 'transfer_req', 'hr_card','prof_change_qiwa']:
                line.service_request_id.write({
                    'upload_payment_doc': line.confirmation_doc,
                    'payment_doc_ref': line.confirmation_doc_ref
                    })
            line.state = 'done'
            # Set dynamic_action_status based on conditions
            if line.service_request_id.service_request == 'hr_card':
                if line.service_request_id.state == 'approved':
                    line.service_request_id.dynamic_action_status = "Approved by Finance Manager.Document upload is pending by second govt employee."
                    line.service_request_id.action_user_id = line.service_request_id.second_govt_employee_id.user_id.id
                    line.service_request_id.write({'processed_date': fields.Datetime.now()})

            elif line.service_request_id.service_request == 'transfer_req':
                line.service_request_id.dynamic_action_status = "Approved by Finance Manager. Process to be completed by second govt employee"
                line.service_request_id.action_user_id = line.service_request_id.second_govt_employee_id.user_id.id
                line.service_request_id.write({'processed_date': fields.Datetime.now()})
            elif line.service_request_id.service_request == 'prof_change_qiwa' and (
                line.service_request_id.billable_to_aamalcom or line.service_request_id.billable_to_client):
                if line.service_request_id.state == 'approved':
                    line.service_request_id.dynamic_action_status = "Approved by Finance Manager.Second Govt employee needs to be assigned by PM"
                    line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
                    line.service_request_id.write({'processed_date': fields.Datetime.now()})
            elif line.service_request_id.service_request in ['iqama_renewal', 'prof_change_qiwa']:
                line.service_request_id.dynamic_action_status = "Service request approved by Finance Team. Second govt employee need to be assigned by PM"
                line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
                line.service_request_id.write({'processed_date': fields.Datetime.now()})

            elif line.service_request_id.service_request not in ['transfer_req', 'hr_card', 'iqama_renewal', 'prof_change_qiwa']:
                line.service_request_id.dynamic_action_status = "Service request approved by Finance Team. First govt employee need to be assigned by PM"
                line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
                line.service_request_id.write({'processed_date': fields.Datetime.now()})







