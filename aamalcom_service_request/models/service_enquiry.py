from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('passport_info_update', 'Passport Information Update')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'passport_info_update': 'cascade'}
    )
    
    process_kind = fields.Selection([('muqeem_online', 'Muqeem(Online Process)'),('jawazat_manual', 'Jawazat(Manual Process)')], string="Process Type", store=True)
    upload_new_passport_doc = fields.Binary(string="New Passport Document")
    upload_new_passport_doc_file_name = fields.Char(string="New Passport Doc")
    upload_old_passport_doc = fields.Binary(string="Old Passport Document")
    upload_old_passport_doc_file_name = fields.Char(string="Old Passport Doc")
    upload_muqeem_doc = fields.Binary(string="Muqeem Document")
    upload_muqeem_doc_file_name = fields.Char(string="Muqeem Document")
    muqeem_doc_ref = fields.Char(string="Ref No.*")
    muqeem_points = fields.Integer(string="Points")
    final_muqeem_cost = fields.Monetary(
        string="Final Muqeem Points Cost (with VAT)",
        currency_field='currency_id',
        compute='_compute_final_muqeem_cost',
    )

    @api.onchange('final_muqeem_cost')
    def _update_muqeem_pricing_line(self):
        for line in self:
            if line.final_muqeem_cost:
                line.service_enquiry_pricing_ids += self.env['service.enquiry.pricing.line'].create({
                        'name': 'Muqeem Fee',
                        'amount':line.final_muqeem_cost,
                        'service_enquiry_id': line.id
                        })
                
    @api.depends('muqeem_points')
    def _compute_final_muqeem_cost(self):
        for record in self:
            if record.muqeem_points:
                base_cost = record.muqeem_points * 0.2
                vat_cost = base_cost * 0.15
                total = base_cost + vat_cost
                record.final_muqeem_cost = round(total, 2)
            else:
                record.final_muqeem_cost = 0.0

    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_new_passport_doc' in vals:
            vals['upload_new_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_NewPassportDoc.pdf"
        if 'upload_old_passport_doc' in vals:
            vals['upload_old_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_OldPassportDoc.pdf"
        if 'fee_receipt_doc' in vals:
            vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceiptDoc.pdf"
        if 'upload_muqeem_doc' in vals:
            vals['upload_muqeem_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_new_passport_doc' in vals:
                vals['upload_new_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_NewPassportDoc.pdf"
            if 'upload_old_passport_doc' in vals:
                vals['upload_old_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_OldPassportDoc.pdf"
            if 'fee_receipt_doc' in vals:
                vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceiptDoc.pdf"
            if 'upload_muqeem_doc' in vals:
                vals['upload_muqeem_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemDoc.pdf"
        return super(ServiceEnquiry, self).write(vals) 

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'passport_info_update':
                if not line.upload_new_passport_doc:
                    raise ValidationError(_("Please upload the new passport document."))
                if not line.upload_old_passport_doc:
                    raise ValidationError(_("Please upload the old passport document."))
                spoc_name = self.env.user.company_spoc_id.name if self.env.user.company_spoc_id else 'Unknown SPOC'
                line.dynamic_action_status = _(f"Passport update request submitted for review by")
                line.action_user_id = line.approver_id.user_id.id
        return True
        
    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request in 'passport_info_update':
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt Document")
                if record.upload_muqeem_doc and not record.muqeem_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Muqeem Document")
        return result

    


class ServiceEnquiryPricingLine(models.Model):
    _inherit = 'service.enquiry.pricing.line'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  related="company_id.currency_id", help="The payment's currency.")
