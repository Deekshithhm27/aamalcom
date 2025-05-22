from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
           ('iqama_correction', 'Iqama Correction')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'iqama_correction': 'cascade'}
    )

    type_of_request = fields.Char(string="Type of Request")
    attached_doc = fields.Binary(string="Attachment Document")
    upload_noc_doc = fields.Binary(string="Upload NOC Document")
    upload_noc_doc_file_name = fields.Char(string="NOC Document")
    noc_doc_ref = fields.Char(string="Ref No.*")
    process_of_type = fields.Selection([('process_by_employee', 'Process By Employee'),('process_by_gro', 'Process By GRO')], string="Process Type", store=True)
    
    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'iqama_correction':
                if not record.type_of_request:
                    raise ValidationError("Kindly update the Type of Request.")

    def action_first_govt_emp_submit(self):
        for record in self:
            if record.service_request == 'iqama_correction':
                record.state = 'submitted'
                employee_name = record.employee_id.name or 'Unknown Employee'
                company_spoc_name = self.env.user.company_spoc_id.name or "Unknown PM"
                record.dynamic_action_status = f"Documents Uploaded by {employee_name} first govt employee. PM {company_spoc_name} need to review"
                record.submit_clicked = True


    def open_assign_employee_wizard(self):
        for line in self:
            if line.service_request == 'iqama_correction':
                # Dynamic level based on state and assigned_govt_emp_two
                if line.state == 'submitted':
                    level = 'level1'
                if line.state == 'payment_done' and not line.assigned_govt_emp_two:
                    level = 'level1'
                if line.state == 'payment_done' and line.assigned_govt_emp_two:
                    level = 'level2'
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
        return super(ServiceEnquiry, self).open_assign_employee_wizard()

    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_muqeem_points_doc' in vals:
            vals['upload_muqeem_points_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPointsDoc.pdf"
        if 'upload_noc_doc' in vals:
            vals['upload_noc_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CorrectionDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_muqeem_points_doc' in vals:
                vals['upload_muqeem_points_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPointsDoc.pdf"
            if 'upload_noc_doc' in vals:
                vals['upload_noc_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPointsDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'iqama_correction':
                if record.upload_muqeem_doc and not record.muqeem_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Muqeem Points Document")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
        return result

    def action_process_complete_gro(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'iqama_correction':
                if record.upload_confirmation_of_exit_reentry and not record.confirmation_of_exit_reentry_ref:
                    raise ValidationError("Kindly Update Reference Number for Confirmation Document")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
        return result
      