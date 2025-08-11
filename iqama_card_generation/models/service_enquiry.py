from odoo import models, fields, api

class IqamaDocument(models.Model):
    _name = 'qiwa.document'
    _description = 'Qiwa Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _order = 'id desc'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,domain="[('client_parent_id','=',client_parent_id)]")
    iqama_no = fields.Char(string="Iqama No")
    identification_id = fields.Char(string='Border No.')
    passport_no = fields.Char(string='Passport No')
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    process_type = fields.Selection([('automatic','Automatic'),('manual','Manual')],string="Process Type",default="manual",copy=False)
    latest_existing_request_id = fields.Boolean(string='Latest Existing Request ID',default=False,copy=False)
    latest_existing_request_name = fields.Char(string='Latest Existing Request Name', readonly=True,copy=False)
    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa'),('twv_request','Temporary Work Visa')],string="Service Request Type",tracking=True,copy=False)
    service_request_config_id = fields.Many2one('service.request.config',string="Service Request",domain="[('service_request_type','=',service_request_type)]",copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed'),
        
    ], string='State', default='draft', tracking=True)
    fee_receipt_doc = fields.Binary(string="Fee Receipt Document")
    fee_receipt_doc_file_name = fields.Char(string="Fee Receipt File Name")
    fee_receipt_doc_ref = fields.Char(string="Ref No.*")

    confirmation_doc = fields.Binary(string="Confirmation Document")
    confirmation_doc_file_name = fields.Char(string="Confirmation Document File Name")
    confirmation_doc_ref = fields.Char(string="Ref No.*")

    iqama_scanned_doc = fields.Binary(string="Iqama Scanned Document")
    iqama_scanned_doc_file_name = fields.Char(string="Iqama Scanned Document File Name")
    iqama_scanned_doc_ref = fields.Char(string="Ref No.*")

    iqma_card_generation_type = fields.Selection([
        ('iqama_print', 'Iqama Print'),
    ], string='Service Request', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    muqeem_points = fields.Integer(string="Points")
    final_muqeem_cost = fields.Monetary(
        string="Final Muqeem Points Cost (with VAT)",
        currency_field='currency_id',
        compute='_compute_final_muqeem_cost',
    )

    # @api.onchange('final_muqeem_cost')
    # def _update_muqeem_pricing_line(self):
    #     for line in self:
    #         if line.final_muqeem_cost:
    #             line.service_enquiry_pricing_ids += self.env['service.enquiry.pricing.line'].create({
    #                     'name': 'Muqeem Fee',
    #                     'amount':line.final_muqeem_cost,
    #                     'service_enquiry_id': line.id
    #                     })
                
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


    # @api.onchange('service_request_config_id')
    # def update_process_type(self):
    #     for line in self:
    #         if line.service_request_config_id:
    #             line.process_type = line.service_request_config_id.process_type
    #         # Passing the latest existing request name in the alert message for visibility,
    #         if line.service_request_config_id and line.employee_id:
    #             latest_existing_request = self.search([
    #                 ('employee_id', '=', line.employee_id.id),
    #                 ('service_request_config_id', '=', line.service_request_config_id.id)
    #             ], limit=1)
                
    service_request = fields.Selection([('iqama_print', 'Iqama Print')],string="Service Requests",related="service_request_config_id.service_request",store=True,copy=False)
    @api.onchange('employee_id')
    def update_service_request_type_from_employee(self):
        for line in self:
            if line.employee_id:
                line.service_request_type = line.employee_id.service_request_type
                line.iqama_no = line.employee_id.iqama_no
                line.identification_id = line.employee_id.identification_id
                line.passport_no = line.employee_id.passport_id

    def action_confirm_documents(self):
           for line in self:
               if line.fee_receipt_doc and not line.fee_receipt_doc_ref:
                   raise ValidationError("Kindly Update Reference Number for Fee Receipt Document")
               if line.confirmation_doc and not line.confirmation_doc_ref:
                   raise ValidationError("Kindly Update Reference Number for Confirmation Document")
               line.state = 'done'
    
