from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('iqama_correction', 'Correction of Personal Information - (Iqama/Muqeem)')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'iqama_correction': 'cascade'}
    )
    state = fields.Selection(selection_add=[('spl_jawazat', 'Waiting from SPL Jawazat for Delivery'),('waiting_jawazat_approval', 'Waiting Jawazat Approval'),('doc_by_gre', 'Document upload Pending by government employee')], ondelete={'spl_jawazat': 'cascade','waiting_jawazat_approval':'cascade'})
    iqama_name_correction_type = fields.Selection([('name_correction', 'Name Correction'),
        ('martial_status', 'Marital Status'),
        ('birth_country', 'Birth Country'),
        ('change_photo', 'Change Photo')], string="Request Type", store=True)
    name_correction_status = fields.Selection([('online_name_correction', 'Online'),
        ('offline_name_correction', 'Offline')], string="Name Correction Status", store=True)
    iqama_document = fields.Binary(string="Iqama Copy",compute='_compute_employee_documents', store=False, attachment=False,readonly=True)
    passport_document = fields.Binary(string="Passport Copy",compute='_compute_employee_documents', store=False, attachment=False,readonly=True)
    # fields for file names
    iqama_document_file_name = fields.Char(string="Iqama File Name")
    passport_document_file_name = fields.Char(string="Passport File Name")
    is_reprint = fields.Boolean(string="Re-Print")
    is_no_print = fields.Boolean(string="No Print")
    inside_ksa = fields.Boolean(string="Inside KSA")
    outside_ksa = fields.Boolean(string="Outside KSA")
    embassy = fields.Boolean(string="Embassy")
    mofa_ksa = fields.Boolean(string="MOFA KSA")
    upload_embassy_document = fields.Binary(string="Embassy Document")
    upload_mofa_ksa_document = fields.Binary(string="MOFA KSA Document")
    upload_saudi_consultant_document = fields.Binary(string="Marriage Certificate(Saudi Consulate)")
    upload_mofa_home_document = fields.Binary(string="Marriage Certificate(MOFA Home Country)")
    upload_scanned_iqama_document = fields.Binary(string="Iqama Document")
    upload_scanned_iqama_file_name = fields.Char(string="Iqama Document")
    scanned_iqama_document_ref = fields.Char(string="Ref No.*")
    upload_noc_doc = fields.Binary(string="Upload NOC Document")
    upload_noc_doc_file_name = fields.Char(string="NOC Document")
    noc_doc_ref = fields.Char(string="Ref No.*")
    upload_coc_doc = fields.Binary(string="Upload COC Document")
    upload_coc_doc_file_name = fields.Char(string="NOC Document")
    coc_doc_ref = fields.Char(string="Ref No.*")
    upload_muqeem_document = fields.Binary(string="Muqeem Document")
    upload_muqeem_document_file_name = fields.Char(string="Muqeem Document")
    muqeem_document_ref = fields.Char(string="Ref No.*")
    fee_receipt_doc = fields.Binary(string="Fee Receipt Document") 
    fee_receipt_doc_ref = fields.Char(string="Ref No.*") 
    iqama_muqeem_points = fields.Integer(string="Points")
    iqama_final_muqeem_cost = fields.Monetary(
        string="Final Muqeem Points Cost (with VAT)",
        currency_field='currency_id',
        compute='_compute_iqama_final_muqeem_cost',
    )

    @api.onchange('is_reprint', 'is_no_print')
    def _onchange_print_options(self):
        for record in self:
            if record.is_reprint:
                record.is_no_print = False
            elif record.is_no_print:
                record.is_reprint = False

    @api.onchange('inside_ksa', 'outside_ksa')
    def _onchange_ksa_options(self):
        for record in self:
            if record.inside_ksa:
                record.outside_ksa = False
            elif record.outside_ksa:
                record.inside_ksa = False


    @api.onchange('iqama_final_muqeem_cost')
    def _update_iqama_muqeem_pricing_line(self):
        for line in self:
            if line.iqama_final_muqeem_cost:
                line.service_enquiry_pricing_ids += self.env['service.enquiry.pricing.line'].create({
                        'name': 'Muqeem Fee(Iqama)',
                        'amount':line.iqama_final_muqeem_cost,
                        'service_enquiry_id': line.id
                        })
                
    @api.depends('iqama_muqeem_points')
    def _compute_iqama_final_muqeem_cost(self):
        for record in self:
            if record.iqama_muqeem_points:
                base_cost = record.iqama_muqeem_points * 0.2
                vat_cost = base_cost * 0.15
                total = base_cost + vat_cost
                record.iqama_final_muqeem_cost = round(total, 2)
            else:
                record.iqama_final_muqeem_cost = 0.0
    
    @api.depends('employee_id')
    def _compute_employee_documents(self):
            """ Computes Iqama and Passport documents from the employee master record. """
            for record in self:
                if record.employee_id:
                    # The employee master fields are 'iqama_copy' and 'passport_copy'
                    record.iqama_document = record.employee_id.iqama_copy
                    record.passport_document = record.employee_id.passport_copy
                else:
                    record.iqama_document = False
                    record.passport_document = False
                    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_noc_doc' in vals:
            vals['upload_noc_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_NOCDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_noc_doc' in vals:
                vals['upload_noc_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_NOCDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    @api.onchange('iqama_name_correction_type')
    def _onchange_iqama_name_correction_type(self):
        """
        Automatically selects 'COC (Online)' type when 'Change Photo' is chosen
        """
        if self.service_request == 'iqama_correction' and self.iqama_name_correction_type == 'change_photo':
            coc_online_record = self.env['letter.print.type'].search([('name', '=', 'COC (Online)')], limit=1)
            if coc_online_record:
                self.letter_print_type_id = [(6, 0, [coc_online_record.id])]
            else:
                self.letter_print_type_id = False
        
    
    def action_submit_payment_confirmation(self):
        super(ServiceEnquiry, self).action_submit_payment_confirmation()
        for record in self:
            if record.service_request == 'iqama_correction':
                record.dynamic_action_status = "PM needs to close the ticket."
                record.action_user_id=record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    
    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'iqama_correction':
                if not (record.aamalcom_pay or record.self_pay or record.employee_pay):
                    raise ValidationError('Please select who needs to pay fees.')
                if record.aamalcom_pay and not (record.billable_to_client or record.billable_to_aamalcom):
                    raise ValidationError(
                                'Please select at least one billing detail when Fees to be paid by Aamalcom is selected.'
                            )
                if not record.passport_document or not record.iqama_document:
                    raise ValidationError(
                        "Please update iqama and passport document in master record."
                    )
                if not record.iqama_name_correction_type:
                    raise ValidationError("Kindly update the any one Type of Request.")
                # === START: Validation for Martial Status / Birth Country (based on XML) ===
                if record.iqama_name_correction_type in ('martial_status', 'birth_country'):
                    # 1. Check if at least one location (Inside/Outside KSA) is selected
                    if not (record.inside_ksa or record.outside_ksa):
                        raise ValidationError("Kindly select  'Inside KSA' or 'Outside KSA'.")
                    # 2. Validation for Inside KSA:
                    if record.inside_ksa:
                        # If inside KSA is selected, EITHER Embassy OR MOFA KSA must be true.
                        if not record.embassy or not record.mofa_ksa:
                            raise ValidationError("Since 'Inside KSA' is selected, you must choose  'Embassy' and 'MOFA KSA'.")  
                        if record.embassy and not record.upload_embassy_document:
                            raise ValidationError("The 'Embassy' option requires the 'Upload Embassy Document'.")  
                        if record.mofa_ksa and not record.upload_mofa_ksa_document:
                            raise ValidationError("The 'MOFA KSA' option requires the 'Upload MOFA KSA Document'.")
                    # 3. Validation for Outside KSA:
                    if record.outside_ksa:
                        # If outside KSA is selected, both documents are mandatory
                        if not record.upload_saudi_consultant_document:
                            raise ValidationError("Since 'Outside KSA' is selected, the 'Upload Saudi Consultant Document' is mandatory.")
                        
                        if not record.upload_mofa_home_document:
                            raise ValidationError("Since 'Outside KSA' is selected, the 'Upload MOFA Home Document' is mandatory.")
                # === END: Validation for Martial Status / Birth Country ===
                # === START: Validation for Change Photo COC types ===
                if record.iqama_name_correction_type == 'change_photo':
                    # NOTE: Assuming 'letter_print_type_id' field exists and is used for COC selection
                    selected_types = record.letter_print_type_id.mapped('name')
                    valid_types = {'COC (Online)'}
                    forbidden_types = {'MOFA (Stamp)', 'Letter-Head','COC (Stamp)'} # Add other non-COC types here
                    # 1. Check if ANY forbidden type is selected
                    if set(selected_types) & forbidden_types:
                        raise ValidationError(
                            'When the Request Type is "Change Photo", you can only select "COC (Online)". Other types are not permitted.'
                            )                
                    # 2. Check if AT LEAST ONE valid type is selected
                    if not (set(selected_types) & valid_types):
                        raise ValidationError(
                                'When the Request Type is "Change Photo", you must select either "COC (Online)" to proceed.'
                                        )
                # === END: Validation for Change Photo COC types ===
                record.dynamic_action_status = "PM needs to assign employee."
                record.action_user_id=record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})


    def action_iqama_correction_submit_for_approval(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                if not record.scanned_iqama_document_ref:
                    raise ValidationError("Kindly update refernce number for Iqama Document")
                if not record.iqama_muqeem_points:
                    raise ValidationError("Kindly update  Muqeem Points")
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
                record.write({'processed_date': fields.Datetime.now()})

    def open_assign_employee_wizard(self):
        """ super method to add a new condition for `exit_reentry_issuance_ext` service request. """
        result = super(ServiceEnquiry, self).open_assign_employee_wizard()
        for line in self:
            if line.service_request == 'iqama_correction':
                # Dynamic level based on state and assigned_govt_emp_two
                department_ids = []
                if line.state == 'approved':
                    level = 'level1'
                if line.state == 'submitted':
                    level = 'level1'
                # Sorting and picking department line based on level
                req_lines = line.service_request_config_id.service_department_lines
                sorted_lines = sorted(req_lines, key=lambda l: l.sequence)
                for lines in sorted_lines:
                    if level == 'level1':
                        department_ids.append((4, lines.department_id.id))
                        break
                    elif level == 'level2' and lines.sequence == 2:
                        department_ids.append((4, lines.department_id.id))
                        break
                return {
                'name': 'Select Employee',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.selection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_department_ids': department_ids,
                    'default_assign_type': 'assign',
                    'default_levels': level,
                },
            }
            
        return result

    def action_pm_review(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                if record.iqama_name_correction_type == 'name_correction':
                    if not record.name_correction_status:
                        raise ValidationError("Kindly update the any Name Correction status")
                # NOTE: The check for muqeem_document_ref is always applied here regardless of type
                if not record.muqeem_document_ref:
                    raise ValidationError("Kindly update refernce number for Muqeem Document")
                if not record.muqeem_points:
                    raise ValidationError("Kindly update  Muqeem Points")
                record.state='submit_to_pm'
                record.dynamic_action_status = "PM needs to select either Re-print No Print"
                record.action_user_id=record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_waiting_jawazat_approval(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                if record.iqama_name_correction_type == 'name_correction':
                    if not record.name_correction_status:
                        raise ValidationError("Kindly update the any Name Correction status")
                if record.iqama_name_correction_type == 'change_photo':
                    if not record.upload_noc_doc:
                        raise ValidationError("For 'Change Photo' requests, the 'Upload NOC Document' is required to proceed.")         
                    if not record.noc_doc_ref:
                        raise ValidationError("For 'Change Photo' requests, kindly update the 'Ref No.*' for the NOC Document.")
                    if not record.fee_receipt_doc:
                        raise ValidationError("For 'Change Photo' requests, the 'Upload Fee Receipt Document' is required to proceed.")        
                    if not record.fee_receipt_doc_ref:
                        raise ValidationError("For 'Change Photo' requests, kindly update the 'Ref No.*' for the fee receipt Document.")
                    if not record.upload_coc_doc:
                        raise ValidationError("For 'Change Photo' requests, the 'Upload COC Document' is required to proceed.")         
                    if not record.coc_doc_ref:
                        raise ValidationError("For 'Change Photo' requests, kindly update the 'Ref No.*' for the COC Document.")

                record.state='waiting_jawazat_approval'
                record.dynamic_action_status = "Waiting for Jawazat approval"
                record.action_user_id=record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_reviewed_by_pm_iqama_correction(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                if not (record.is_reprint or record.is_no_print):
                    raise ValidationError("Kindly select either Re-print or No Print.")
                record.state='doc_by_gre'
                record.dynamic_action_status = "Documents upload Pending by government employee."
                record.action_user_id=record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_reviewed_by_gre_send_to_client(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                if not record.scanned_iqama_document_ref:
                    raise ValidationError("Kindly update refernce number for Iqama Document")
                record.state='payment_initiation'
                record.dynamic_action_status = "Payment Documents Upload Pending by Client"
                partner_id = record.client_id.id
                user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
                if user:
                    record.action_user_id = user.id
                record.write({'processed_date': fields.Datetime.now()})


    def action_reviewed_by_gre_iqama_correction(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                record.state='done'
                record.dynamic_action_status = "Process Completed"
                record.write({'processed_date': fields.Datetime.now()})


    def action_process_complete_iqama_if_reprint(self):
            for record in self:
                if record.service_request == 'iqama_correction':
                    if record.service_enquiry_pricing_ids:
                        invoice_line_ids = []
                        for line in record.service_enquiry_pricing_ids:
                            invoice_line_ids.append((0, 0, {
                                'name': line.name,
                                'employee_id': record.employee_id.id, 
                                'price_unit': line.amount,
                                'quantity': 1,
                                'service_enquiry_id': record.id
                            }))
                        move_vals = {
                            'client_id': record.client_id.id,
                            'client_parent_id': record.client_id.parent_id.id,
                            'service_enquiry_id': record.id,
                            'employee_id': record.employee_id.id,
                            'move_type': 'service_ticket', 
                            'invoice_line_ids': invoice_line_ids,
                        }

                        self.env['draft.account.move'].create(move_vals)

                    record.state = 'done'  
                    record.dynamic_action_status = "Process Completed"
                    record.write({'processed_date': fields.Datetime.now()})

    def action_process_complete_iqama_if_no_reprint(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.write({'processed_date': fields.Datetime.now()})

    def action_process_complete_iqama(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.write({'processed_date': fields.Datetime.now()})