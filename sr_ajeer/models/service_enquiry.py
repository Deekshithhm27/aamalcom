from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('ajeer_permit', 'Ajeer Permit')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'ajeer_permit': 'cascade'}
        
    )
    ajeer_permit_type = fields.Selection([('secondement_permit', 'Secondment Ajeer Permit'),('contracting_permit', 'Ajeer Contracting Permit')], string="Ajeer Permit Type", store=True)
    mol_number = fields.Char(string="MoL Number")
    cr_number = fields.Char(string="CR Number")
    location = fields.Char(string="Location")
    saddad_number = fields.Char(string="Saddad Number")
    upload_screenshot_of_saddad = fields.Binary(string="Saddad Document")
    upload_screenshot_of_saddad_file_name=fields.Char(string="Saddad Document")
    upload_ajeer_permit_doc=fields.Binary(string="Ajeer Permit Document")
    ajeer_permit_doc_ref=fields.Char(string="Ref No.*")
    upload_ajeer_permit_doc_file_name=fields.Char(string="Ajeer Permit Document")
    upload_invoice_payment_doc = fields.Binary(string="Invoice Payment Document")
    invoice_payment_ref_no = fields.Char(string="Ref No.*")


    @api.onchange('ajeer_permit_type')
    def _onchange_ajeer_permit_type(self):
        if self.ajeer_permit_type == 'secondement_permit':
            return {'domain': {'employment_duration': [('name', 'ilike', 'Secondment Ajeer permit'),('service_request_type','=',self.service_request_type)]}}  # Matches any duration containing 'SAP'
        elif self.ajeer_permit_type == 'contracting_permit':
            return {'domain': {'employment_duration': [('name', 'ilike', 'Contracting Ajeer permit'),('service_request_type','=',self.service_request_type)]}}  # Matches any duration containing 'ACP'
    
    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'ajeer_permit' :
                if not line.aamalcom_pay and not line.self_pay:
                    raise ValidationError('Please select who needs to pay fees.')
            if line.aamalcom_pay and not (line.billable_to_client or line.billable_to_aamalcom):
                raise ValidationError('Please select at least one billing detail when Fees to be paid by Aamalcom is selected.')
            if line.service_request == 'ajeer_permit':
                if not line.mol_number or not line.cr_number:
                     raise ValidationError("MoL Number and CR Number are required before submission.")
            if line.service_request == 'ajeer_permit':
                if not line.ajeer_permit_type :
                    raise ValidationError("Please select at least one: Either Secondment Ajeer Permit or Ajeer Contracting Permit.")
                if not line.employment_duration:
                    raise ValidationError('Please select Duration.')
    def action_require_payment_confirmation(self):
        super(ServiceEnquiry, self).action_require_payment_confirmation()
        for record in self:
            if record.service_request == 'ajeer_permit':
                # if record.upload_screenshot_of_saddad and not record.saddad_number:
                #     raise ValidationError("Kindly Update Saddad Number")
                
                record.write({'processed_date': fields.Datetime.now()})
                
    def action_submit_payment_confirmation(self):
        super(ServiceEnquiry, self).action_submit_payment_confirmation()
        for record in self:
            if record.service_request == 'ajeer_permit':
                record.dynamic_action_status=f"Document upload pending by first govt employee"
                record.action_user_id=record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_screenshot_of_saddad' in vals:
            vals['upload_screenshot_of_saddad_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SaddadDoc.pdf"
        if 'upload_ajeer_permit_doc' in vals:
            vals['upload_ajeer_permit_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AjeerPermitDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_screenshot_of_saddad' in vals:
                vals['upload_screenshot_of_saddad_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SaddadDoc.pdf"
            if 'upload_ajeer_permit_doc' in vals:
                vals['upload_ajeer_permit_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AjeerPermitDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    def action_ajeer_permit_submit_for_approval(self):
        for record in self:
            if record.service_request == 'ajeer_permit':
                # if record.upload_screenshot_of_saddad and not record.saddad_number:
                #     raise ValidationError("Kindly Update Saddad Number")
                record.state = 'waiting_op_approval'
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.dynamic_action_status = f"Waiting for approval by OM"
                record.action_user_id = employee.user_id
                record.write({'processed_date': fields.Datetime.now()})
                record.send_email_to_op()

    def update_pricing(self):
        result = super(ServiceEnquiry, self).update_pricing()
        for record in self:
            pricing_id = self.env['service.pricing'].search(
                [('service_request_type', '=', record.service_request_type),
                 ('service_request', '=', record.service_request)], limit=1)
            if record.service_request == 'ajeer_permit':
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

    
    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'ajeer_permit':
                if record.upload_ajeer_permit_doc and not record.ajeer_permit_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Ajeer Permit Document")
                if record.upload_invoice_payment_doc and not record.invoice_payment_ref_no:
                    raise ValidationError("Kindly Update Reference Number for Invoice Payment  Document")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False
                record.write({'processed_date': fields.Datetime.now()})
        return result
            
    

    
       
    