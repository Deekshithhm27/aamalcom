from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('exit_reentry_issuance','Exit Rentry Issuance'),('exit_reentry_issuance_ext','Exit Re-entry(Extension)')
        ],
        string="Service Request",
        store=True,
        copy=False,ondelete={'exit_reentry_issuance_ext': 'cascade','exit_reentry_issuance': 'cascade'}
    )


    # Fields - Exit Rentry issuance
    exit_type = fields.Selection([('single', 'Single'),('multiple', 'Multiple')], string="Type", store=True)
    to_be_issued_date = fields.Date(string="To be issued from")
    upload_confirmation_of_exit_reentry = fields.Binary(string="Upload Confirmation of Exit re-entry", store=True)
    upload_confirmation_of_exit_reentry_file_name = fields.Char(string="Upload Confirmation of Exit re-entry")
    confirmation_of_exit_reentry_ref = fields.Char(string="Ref No.*")
    upload_exit_reentry_visa = fields.Binary(string="Exit Re-entry Visa")
    upload_exit_reentry_visa_file_name = fields.Char(string="Exit Re-entry Visa File Name")
    exit_reentry_visa_ref = fields.Char(string="Ref No.*")

    # Fields - Exit Re-entry (Extension)
    service_request_id = fields.Many2one('service.enquiry',order='create_date DESC', )
    ere_extension_doc = fields.Binary()
    ere_extension_doc_file_name = fields.Char()
    ere_extension_doc_ref = fields.Char()
    is_client_spoc = fields.Boolean(compute='_compute_is_client_spoc', store=False)

    
    @api.onchange('exit_type')
    def _onchange_exit_type(self):
        for line in self:
            if line.service_request in ('exit_reentry_issuance','exit_reentry_issuance_ext'):
                if self.exit_type == 'single':
                    return {'domain': {'employment_duration': [('name', 'ilike', 'SER'),('service_request_type','=',self.service_request_type)]}}  # Matches any duration containing 'SER'
                elif self.exit_type == 'multiple':
                    return {'domain': {'employment_duration': [('name', 'ilike', 'MER'),('service_request_type','=',self.service_request_type)]}}  # Matches any duration containing 'MER'
        
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'confirmation_doc' in vals:
            vals['confirmation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ConfirmationDoc.pdf"
        if 'ere_extension_doc' in vals:
            vals['ere_extension_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EREExtendVisaDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'confirmation_doc' in vals:
                vals['confirmation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ConfirmationDoc.pdf"
            if 'ere_extension_doc' in vals:
                vals['ere_extension_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EREExtendVisaDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    @api.onchange('upload_confirmation_of_exit_reentry', 'upload_exit_reentry_visa', 'confirmation_doc',
                  'ere_extension_doc', )
    def ere_document_uploaded(self):
        for record in self:
            if record.service_request == 'exit_reentry_issuance':
                if record.upload_confirmation_of_exit_reentry and record.upload_exit_reentry_visa:
                    record.doc_uploaded = True
            if record.service_request == 'exit_reentry_issuance_ext':
                if record.confirmation_doc and record.ere_extension_doc:
                    record.doc_uploaded = True

    # The client SPOC submits, Updates pricing for Exit Re-Entry Issuance and its extension.
    def update_pricing(self):
        result = super(ServiceEnquiry, self).update_pricing()
        for record in self:
            pricing_id = self.env['service.pricing'].search(
                [('service_request_type', '=', record.service_request_type),
                 ('service_request', '=', record.service_request)], limit=1)
            if record.service_request == 'exit_reentry_issuance_ext' or record.service_request == 'exit_reentry_issuance':
                print("-------pridinc id",pricing_id)
                if pricing_id:
                    for p_line in pricing_id.pricing_line_ids:
                        if p_line.duration_id == record.employment_duration:
                            record.service_enquiry_pricing_ids.create({
                                'name':f"{p_line.duration_id.name}",
                                'service_enquiry_id':record.id,
                                'service_pricing_id':pricing_id.id,
                                'service_pricing_line_id':p_line.id,
                                'amount':p_line.amount,
                                'remarks':p_line.remarks
                            })
                else:
                    raise ValidationError(_('Service Pricing is not configured properly. Kindly contact your Accounts Manager'))
        return result

    @api.onchange('employee_id',)
    def _onchange_employee_id(self):
        for line in self:
            # domain to filter based on ere and employee and completed state
            if line.employee_id:
                return {
                    'domain': {
                        'service_request_id': [
                            ('service_request', '=', 'exit_reentry_issuance'),
                            ('employee_id', '=', line.employee_id.id),
                            ('state', '=', 'done')
                        ]
                    }
                }

    @api.onchange('service_request_id')
    def onchange_service_request_id(self):
        for line in self:
            if line.service_request == 'exit_reentry_issuance_ext':
                # Exit Rentry issuance data auto fill
                line.exit_type = line.service_request_id.exit_type
                line.exit_reentry_visa_ref = line.service_request_id.exit_reentry_visa_ref
                line.write({
                    'upload_exit_reentry_visa': line.service_request_id.upload_exit_reentry_visa,
                    'upload_exit_reentry_visa_file_name': line.service_request_id.upload_exit_reentry_visa_file_name
                })

    def action_submit(self):
        result = super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'exit_reentry_issuance_ext':
                if not record.service_request_id:
                    raise ValidationError('Please select Valid ERE.')
                if not record.employment_duration:
                    raise ValidationError('Please select Duration.')
                if not (record.aamalcom_pay or record.self_pay or record.employee_pay):
                    raise ValidationError('Please select who needs to pay fees.')
                if record.aamalcom_pay and not (record.billable_to_client or record.billable_to_aamalcom):
                    raise ValidationError(
                        'Please select at least one billing detail when Fees to be paid by Aamalcom is selected.'
                    )
            if record.service_request == 'exit_reentry_issuance_ext' and record.aamalcom_pay:
                record.state = 'waiting_op_approval'
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.dynamic_action_status = f"Waiting for approval by OM"
                record.action_user_id = employee.user_id
        return result

    # Initial flow of exit_reentry_issuance
    def action_submit_initiate(self):
        result = super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'exit_reentry_issuance':
                if not record.employment_duration:
                    raise ValidationError('Please select Duration.')
            if record.service_request == 'exit_reentry_issuance':
                if not (record.aamalcom_pay or record.self_pay or record.employee_pay):
                    raise ValidationError('Please select who needs to pay fees.')
                if record.aamalcom_pay and not (record.billable_to_client or record.billable_to_aamalcom):
                    raise ValidationError(
                        'Please select at least one billing detail when Fees to be paid by Aamalcom is selected.'
                    )
        return result

    def action_finance_approved(self):
        result = super(ServiceEnquiry, self).action_finance_approved()
        for record in self:
            if record.aamalcom_pay and record.service_request == 'exit_reentry_issuance_ext':
                record.assign_govt_emp_one = True
        return result

    def action_submit_payment_confirmation(self):
        result = super(ServiceEnquiry, self).action_submit_payment_confirmation()
        for record in self:
            if record.service_request == 'exit_reentry_issuance_ext':
                if record.upload_payment_doc and not record.payment_doc_ref:
                    raise ValidationError("Kindly Update Reference Number For Payment Confirmation Document")
                record.dynamic_action_status = 'Payment done by client spoc. Documents upload pending by first employee'
                record.action_user_id = record.first_govt_employee_id.user_id.id
        return result

    

    def open_assign_employee_wizard(self):
        """ super method to add a new condition for `exit_reentry_issuance_ext` service request. """
        result = super(ServiceEnquiry, self).open_assign_employee_wizard()
        for record in self:
            if record.service_request == 'exit_reentry_issuance_ext' and record.state == 'approved' or record.state == 'payment_done':
                # level = 'level1'
                department_ids = []
                req_lines = record.service_request_config_id.service_department_lines
                sorted_lines = sorted(req_lines, key=lambda line: line.sequence)
                for lines in sorted_lines:
                    # if level == 'level1':
                    department_ids.append((4, lines.department_id.id))

                result.update({
                    'name': 'Select Employee',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee.selection.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_department_ids': department_ids,
                        'default_assign_type': 'assign',
                        'default_levels': 'level2',
                    },
                })
        return result

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'exit_reentry_issuance':
                if record.upload_confirmation_of_exit_reentry and not record.confirmation_of_exit_reentry_ref:
                    raise ValidationError(
                        "Kindly Update Reference Number for Upload Confirmation of Exit re-entry Document")
                if record.upload_exit_reentry_visa and not record.exit_reentry_visa_ref:
                    raise ValidationError("Kindly Update Reference Number for Exit Re-entry Visa Document")
            if record.service_request == 'exit_reentry_issuance_ext':
                if record.confirmation_doc and not record.confirmation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number For Upload Confirmation Of ERE Extend")
                if record.ere_extension_doc and not record.ere_extension_doc_ref:
                    raise ValidationError("Kindly Update Reference Number For ERE Extend Visa")

            record.state = 'done'  
            record.dynamic_action_status = "Process Completed"  
            record.action_user_id=False      
        return result
