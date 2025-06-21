from odoo import models, fields, api

class ServiceRequestTreasuryInherit(models.Model):
    _inherit = 'service.request.treasury'

    service_request_type = fields.Selection(
        related="service_request_id.service_request",
        store=True,
        readonly=True,
    )
    clinic_name = fields.Char(string="Clinic Name")

    def action_upload_confirmation_medical(self):       
        for line in self:
            if line.service_request_id.service_request == 'medical_blood_test':
                # Upload confirmation_doc to the service.request model
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                line.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})
                # Only modify dynamic_action_status if the state is 'approved'
                if line.service_request_id.state == 'approved':
                    # Set the specific dynamic action status for 'medical_blood_test'
                    line.service_request_id.dynamic_action_status = "Service request approved by Finance Team.1st govt employee Needs to be assigned by PM"
                    line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
                line.state='done'

         
    #This function is used to submit ticket directly to treasury dept skipping, Fm submit button
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.service_request_id.service_request == 'medical_blood_test':
                record.state = 'submitted'
        return records

    def action_details_updated(self):
        for record in self:
            if record.service_request_id.service_request == 'medical_blood_test':
                record.service_request_id.dynamic_action_status = "Waiting for approval by OM"
                record.state = 'updated_by_treasury'
                

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
