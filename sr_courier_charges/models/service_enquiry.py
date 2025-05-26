from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
             ('courier_charges', 'Courier')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'courier_charges': 'cascade'}
    )
    
    upload_courier_doc = fields.Binary(string="Document To Be Couried")
    upload_courier_file_name = fields.Char(string="Couried Document")
    upload_courier_proof_doc = fields.Binary(string="Courier Attached Document")
    upload_courier_proof_doc_file_name = fields.Char(string="Courier Attached Document")
    courier_payment_doc = fields.Binary(string="Payment Confirmation Document")
    courier_ref = fields.Char(string="Ref No.*")
    courier_amount = fields.Integer(string="Courier Amount")
    submit_clicked = fields.Boolean(string="Submit Clicked", default=False)
    tracking_id=fields.Char(string="Tracking ID")
    

    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_courier_doc' in vals:
            vals['upload_courier_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CourierDoc.pdf"
        if 'upload_courier_proof_doc' in vals:
            vals['upload_courier_proof_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CourierAttachedDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_courier_doc' in vals:
                vals['upload_courier_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CourierDoc.pdf"
            if 'upload_courier_proof_doc' in vals:
                vals['upload_courier_proof_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CourierAttachedDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)    

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'courier_charges':
                if not line.upload_courier_doc:
                    raise ValidationError(_("Please upload the Courier document."))
        return True
        

    def action_submit_for_review_courier(self):
        for line in self:
            if line.service_request == 'courier_charges':
                if line.upload_courier_proof_doc and not line.courier_ref:
                    raise ValidationError(_("Kindly Update Reference Number for Attached Courier Document"))
                line.dynamic_action_status = _("Review is Pending by PM")  
                line.state = 'submitted'
                line.submit_clicked = True
    
    

    def action_approve(self):
        for record in self:
            if record.service_request == 'courier_charges':
                    record.state = 'approved'
                    record.dynamic_action_status = "Documents Upload Pending by 1st Govt Employee"
                
    
    
    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'courier_charges':
                if record.upload_payment_doc and not record.payment_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Payment Document")
        return result

class ServiceEnquiryPricingLine(models.Model):
    _inherit = 'service.enquiry.pricing.line'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  related="company_id.currency_id", help="The payment's currency.")
    

    


