from odoo import models, fields, api

class ServiceRequestTreasuryInherit(models.Model):
    _inherit = 'service.request.treasury'

    service_request_type = fields.Selection(
        related="service_request_id.service_request",
        store=True,
        readonly=True,
    )
    clinic_name = fields.Char(string="Clinic Name")

    
    
    def action_upload_confirmation(self):
        super(ServiceRequestTreasuryInherit, self).action_upload_confirmation()
        for line in self:
            if line.service_request_id.service_request == 'medical_blood_test':
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                line.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})
                if line.service_request_id.state == 'submitted_to_treasury':
                    line.service_request_id.dynamic_action_status = "Service request approved by Treasury Team.1st govt employee Needs to be assigned by PM"
                    line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
                line.state = 'done'
                # If the treasury record just became 'done' AND it's a 'medical_blood_test' service,
                # then update the service.enquiry state to 'approved'.
                if line.service_request_id and line.service_request_id.service_request == 'medical_blood_test':
                    line.service_request_id.write({'state': 'approved'})
                    
    #This function is used to submit ticket directly to treasury dept skipping, Fm submit button
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.service_request_id.service_request == 'medical_blood_test':
                record.state = 'passed_to_treasury'
        return records

    def action_details_updated(self):
        for record in self:
            if record.service_request_id.service_request == 'medical_blood_test':
                record.service_request_id.write({'clinic_name': record.clinic_name})
                record.service_request_id.write({'total_price':record.total_amount})
                record.service_request_id.dynamic_action_status = "Waiting for approval by OH"
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.service_request_id.action_user_id = employee.user_id
                record.state = 'updated_by_treasury'

    @api.onchange('service_request_id')
    def _onchange_service_request_id_state(self):
        # This onchange will trigger when service_request_id is set/changed on the form.
        # It's less reliable for syncing states that change on the linked record.
        # The direct write from service.enquiry is more robust.
        if self.service_request_id and self.service_request_id.service_request == 'medical_blood_test' and self.service_request_id.state == 'submitted_to_treasury':
            self.state = 'submitted'
        
                

    #It helps to set state to waiting OH approval after treasury state is set to Updated by treasury
    ## since in between no other dept is involved
    def write(self, vals):
        result = super().write(vals)
        if 'state' in vals and vals['state'] == 'updated_by_treasury':
            for record in self:
                enquiry = record.service_request_id
                if enquiry.service_request == 'medical_blood_test':
                    enquiry.state = 'waiting_op_approval'
        return result
    
    def write(self, vals):
        # Store the old state before the write operation
        old_state_done = self.filtered(lambda r: r.state != 'done' and 'state' in vals and vals['state'] == 'done')

        result = super().write(vals)

        # After the write operation, check for the condition on the records that just changed state to 'done'
        for record in old_state_done:
            if record.service_request_id and record.service_request_id.service_request == 'medical_blood_test':
                # Update the service.enquiry state to 'approved'
                record.service_request_id.write({'state': 'approved'})

        # Original logic from your code for 'updated_by_treasury' state
        if 'state' in vals and vals['state'] == 'updated_by_treasury':
            for record in self:
                enquiry = record.service_request_id
                if enquiry.service_request == 'medical_blood_test':
                    enquiry.state = 'waiting_op_approval'
        return result
