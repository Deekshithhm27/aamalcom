from datetime import date
from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(selection_add=[('muqeem_dropout', 'Muqeem Dropout'),('muqeem_dependents','Dependents Muqeem Details')],
                                       ondelete={'muqeem_dropout': 'cascade','muqeem_dependents': 'cascade'})
    state = fields.Selection(selection_add=[('ere_valid', 'Valid ERE')], ondelete={'ere_valid': 'cascade'})

    is_inside_ksa = fields.Boolean(string="Inside KSA",
                                    help="Indicates whether the employee is Inside KSA (True) or Outside KSA (False).")
    expiry_of_ere = fields.Date(string="Expiry of ERE", help="Expiry date of the employee's ERE")

    muqeem_confirmation_doc = fields.Binary(string="Confirmation Document")
    muqeem_confirmation_doc_file_name = fields.Char(string="Confirmation Document File Name")
    muqeem_confirmation_doc_ref = fields.Char(string="Ref No.*")

    is_resubmission = fields.Boolean(default=False)

    # @api.constrains('is_inside_ksa', 'expiry_of_ere')
    # def _check_outside_ksa(self):
    #     for line in self:
    #         if line.service_request in 'muqeem_dropout':
    #             if line.is_inside_ksa:
    #                 raise ValidationError("Not applicable for employees inside KSA. Only applicable for those outside KSA.")
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'muqeem_confirmation_doc' in vals:
            vals['muqeem_confirmation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'muqeem_confirmation_doc' in vals:
                vals['muqeem_confirmation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)
    
    def action_submit_initiate(self):
        result = super(ServiceEnquiry, self).action_submit_initiate()
        for line in self:
            if line.service_request in 'muqeem_dropout':
                if not line.is_inside_ksa and not line.expiry_of_ere:
                    raise ValidationError("Kindly Update Expiry of ERE")
                if line.is_resubmission:
                    line.dynamic_action_status = 'Ticket resubmitted, Employee needs to be assigned by PM'
                    line.action_user_id = line.approver_id.user_id.id
                    line.write({'processed_date': fields.Datetime.now()})
        return result
        
    @api.onchange('service_request')
    def _onchange_service_request(self):
        for line in self:
            if line.service_request == 'muqeem_dropout':
                line.aamalcom_pay = True

    def action_valid_ere(self):
        """Change status to 'ERE is Valid' and notify the client SPOC"""
        for line in self:
            if line.service_request in 'muqeem_dropout':
                line.state = 'ere_valid'
                line.dynamic_action_status = 'ERE is still valid,Please re initiate this process upon ERE expiry.'
                line.write({'processed_date': fields.Datetime.now()})
                line.assign_govt_emp_one = False
                line.assigned_govt_emp_one = False
                line.is_resubmission = True

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request in 'muqeem_dependents':
                if record.muqeem_confirmation_doc and not record.muqeem_confirmation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Muqeem Dependents Document")
            if record.service_request in 'muqeem_dropout':
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt Document")
                if record.muqeem_confirmation_doc and not record.muqeem_confirmation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Confirmation Document")
                invoice_line_ids = []
                for line in record.service_enquiry_pricing_ids:
                    invoice_line_ids.append((0, 0, {
                        'name': line.name,
                        'employee_id': record.employee_id.id,
                        'price_unit': line.amount,
                        'quantity': 1,
                        'service_enquiry_id': record.id
                    }))

                # Create draft.account.move record
                account_move = self.env['draft.account.move'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id': record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id': record.employee_id.id,
                    'move_type': 'service_ticket',
                    'invoice_line_ids': invoice_line_ids,
                })
        return result
