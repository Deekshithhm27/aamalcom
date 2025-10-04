# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrServiceRequestTreasury(models.Model):
    _name = 'hr.service.request.treasury'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Treasury'
    
    name = fields.Char(
        string='Request ID',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.service.request.treasury')
    )
    service_type = fields.Selection([
        ('iqama_issuance', 'Iqama Issuance - Medical Blood Test'),
        ('exit_reentry', 'Exit Re-entry Issuance'), # Added for your use case
    ], string="Service Request", help="Type of service request from the source document.")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  related="company_id.currency_id", help="The payment's currency.")
    clinic_name = fields.Char(string="Clinic Name")

    # The key change: Using a Reference field for a generic link
    service_request_ref = fields.Reference(
        string="Service Request",
        selection='_get_service_request_models',
        ondelete='cascade',
        tracking=True,
    )
    

    employee_id = fields.Many2one('hr.employee', string="Employee")
    total_amount = fields.Monetary(string="Amount")
    exit_type = fields.Selection([('single', 'Single'), ('multiple', 'Multiple')], string="Exit Type", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted to Treasury'),
        ('passed_to_treasury', 'Passed to Treasury'),
        ('submit_for_approval', 'Waiting for Approval'),
        ('done', 'Done')
    ], string="Status", default='draft', tracking=True)
    confirmation_doc = fields.Binary(string="Confirmation Doc*")
    confirmation_doc_ref = fields.Char(string="Ref No.*")
    issue_date = fields.Date(string='Issue Date')

    # Method to dynamically get models that can be linked to treasury
    @api.model
    def _get_service_request_models(self):
        return [
            ('hr.exit.reentry', 'Exit Re-entry Request'), 
            ('hr.medical.blood.test', 'Medical Blood Test'),
            ('loan.request', 'Loan Request'),
            
        ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.service.request.treasury')
        return super(HrServiceRequestTreasury, self).create(vals_list)

    def action_submit(self):
        self.ensure_one()
        self.state = 'submitted'
        
        # You can keep this logic to update the state of the source document
        if self.service_request_ref:
            self.service_request_ref.state = 'submitted_to_treasury'

    def action_upload_confirmation(self):
        self.ensure_one()
        if not self.confirmation_doc or not self.confirmation_doc_ref or not self.issue_date:
            raise ValidationError("Kindly upload the Confirmation Document, Reference Number, and Issue Date.")      
        if self.service_request_ref and self.service_request_ref._name == 'hr.exit.reentry':
            self.service_request_ref.write({
                'treasury_confirmation_doc': self.confirmation_doc,
                'treasury_confirmation_ref': self.confirmation_doc_ref,
            })
            self.message_post(body=_("Payment Confirmation document uploaded for Exit Re-entry request."))
        if self.service_request_ref and self.service_request_ref._name == 'hr.medical.blood.test':
            self.service_request_ref.write({
                'treasury_confirmation_doc': self.confirmation_doc,
                'treasury_confirmation_ref': self.confirmation_doc_ref,
            })
            self.message_post(body=_("Payment Confirmation document uploaded for Iqama Issuance Medical Blood Test request."))
        self.state = 'done'
        if self.service_request_ref:
            self.service_request_ref.state = 'approved'

    def action_update_treasury(self):
        """
        Updates the state to 'updated_by_treasury' and propagates 
        the final total_amount and clinic_name back to the source document.
        """
        self.ensure_one()
        
        # 1. Update the state of the current Treasury record
        self.state = 'submit_for_approval'
        
        # 2. Update the state of the source (hr.medical.blood.test) record
        if self.service_request_ref and self.service_request_ref._name == 'hr.medical.blood.test':
            self.service_request_ref.write({
                'state': 'submit_for_approval',
                'total_amount': self.total_amount, # Pass back the updated amount
                'clinic_name': self.clinic_name,  # Pass back the updated clinic name
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    def action_view_source_document(self):
        """ Dynamically opens the source document linked by service_request_ref. """
        self.ensure_one()
        if not self.service_request_ref:
            return False

        # The service_request_ref is a recordset (e.g., self.env['loan.request'](2)).
        # We can extract the model name and ID directly from it.
        model_name = self.service_request_ref._name
        record_id = self.service_request_ref.id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Source Document: %s') % model_name,
            'res_model': model_name,
            'res_id': record_id,
            'view_mode': 'form',
            'target': 'current',
        }
