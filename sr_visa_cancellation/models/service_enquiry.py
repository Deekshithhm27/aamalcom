from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, UserError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('visa_cancellation', 'Visa Cancellation')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'visa_cancellation': 'cascade'}

    )
    ref_ev_id = fields.Many2one(
        'service.enquiry',
        string="Ref SR-EV",
        domain="[('service_request', '=', 'new_ev'), ('state', '=', 'done'),('employee_id','=',employee_id)]",
       
    )
    state = fields.Selection(selection_add=[('waiting_for_minitry_approvals', 'Waiting for Ministry Approvals'),('approved_ministry', 'Approved by Ministry')], ondelete={'waiting_for_minitry_approvals': 'cascade','approved_ministry':'cascade'})
    reason_of_cancellation = fields.Text("Reason for Visa Cancellation")
    upload_visa_cancellation_doc = fields.Binary(string="Visa cancellation request document")
    upload_visa_cancellation_doc_file_name = fields.Char(string="Visa cancellation request document")
    visa_cancellation_doc_ref = fields.Char(string="Ref No.*")
    upload_confirmation_visa_doc = fields.Binary(string="Confirmation of visa cancellation document")
    upload_confirmation_visa_file_name = fields.Char(string="confirmation of visa cancellation document")
    confirmation_visa_doc_ref = fields.Char(string="Ref No.*")

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'visa_cancellation':
                line.dynamic_action_status = "PM needs to review and assign employee."
                line.action_user_id=line.approver_id.user_id.id

    def open_assign_employee_wizard(self):
        """Inherit open_assign_employee_wizard to add validation for visa cancellation"""
        for record in self:
            if record.service_request == 'visa_cancellation':
                # Validate required fields for visa cancellation
                if not record.ref_ev_id:
                    raise ValidationError(_("Please select the Reference-EV for visa cancellation request."))
                if not record.reason_of_cancellation:
                    raise ValidationError(_("Please provide the reason for cancellation for visa cancellation request."))
        # Call the parent method
        return super(ServiceEnquiry, self).open_assign_employee_wizard()

    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_visa_cancellation_doc' in vals:
            vals['upload_visa_cancellation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_VisaCancellationDoc.pdf"
        if 'upload_confirmation_visa_doc' in vals:
            vals['upload_confirmation_visa_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_VisaCancellationConfiramtion.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_visa_cancellation_doc' in vals:
                vals['upload_visa_cancellation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_VisaCancellationDoc.pdf"
            if 'upload_confirmation_visa_doc' in vals:
                vals['upload_confirmation_visa_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_VisaCancellationConfiramtion.pdf"
        return super(ServiceEnquiry, self).write(vals)


    def action_submit_to_ministry(self):
        for record in self:
            if record.service_request == 'visa_cancellation':
                if record.upload_visa_cancellation_doc and not record.visa_cancellation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Visa Cancellation Doc")
                record.state = 'waiting_for_minitry_approvals'
                record.dynamic_action_status = "Documents Uploaded by first govt employee. Waiting for Ministry Approvals"
                record.action_user_id = record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_approved_by_ministry(self):
        for record in self:
            if record.service_request == 'visa_cancellation':
                record.state = 'approved_ministry'
                record.dynamic_action_status = "Approved by Ministry, Documents Upload is pending by first govt employee"
                record.action_user_id = record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_submit_to_treasury_visa_cancellation(self):
        """Submit visa cancellation request directly to treasury"""
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for record in self:
            if record.service_request == 'visa_cancellation':
                # Check if a treasury record already exists for this service request
                existing_doc = self.env['service.request.treasury'].sudo().search([
                    ('service_request_id', '=', record.id)
                ], limit=1)
                
                if existing_doc:
                    continue 
                # Create treasury record
                vals = {
                    'service_request_id': record.id,
                    'client_id': record.client_id.id,
                    'client_parent_id': record.client_id.parent_id.id,
                    'employee_id': record.employee_id.id,

                    'total_amount': record.total_amount if hasattr(record, 'total_amount') else 0.0
                }
                service_request_treasury_id = self.env['service.request.treasury'].sudo().create(vals)
                treasury = self.env['service.request.treasury'].sudo().search([
                    ('service_request_id', '=', record.id)
                ], limit=1)
                if treasury:
                    treasury.write({
                        'service_request_config_id':self.service_request_config_id.id,
                        'ref_ev_id': record.ref_ev_id,
                        'reason_of_cancellation':record.reason_of_cancellation
                    })
                if service_request_treasury_id:
                    record.state = 'submitted_to_treasury'
                    record.dynamic_action_status = f'Submitted to Treasury Department by . Review to be done by Treasury'
                    record.gm_approver_id = current_employee
                    finance_manager = self.env['hr.department'].search([('name', 'ilike', 'Finance')], limit=1).manager_id
                    record.action_user_id = finance_manager.user_id
                    record.write({'processed_date': fields.Datetime.now()})
                    # Automatically submit the treasury record
                    service_request_treasury_id.action_submit_to_treasury_visa_cancellation()

   