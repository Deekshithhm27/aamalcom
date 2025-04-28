from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
           ('dependents_ere', 'Dependents ExitRentry')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'dependents_ere': 'cascade'}
    )

    def action_dependents_ere_submit_for_approval(self):
        for record in self:
            if record.service_request == 'dependents_ere':
                record.state = 'waiting_op_approval'
                record.dynamic_action_status = "Waiting for approval by OM"
                record.send_email_to_op()

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()

    @api.model
    def update_pricing(self):
        result = super(ServiceEnquiry, self).update_pricing()
        for record in self:
            pricing_id = self.env['service.pricing'].search(
                [('service_request_type', '=', record.service_request_type),
                 ('service_request', '=', record.service_request)], limit=1)
            if record.service_request == 'dependents_ere':
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
            if record.service_request == 'dependents_ere':
                invoice_line_ids = []
                for line in record.service_enquiry_pricing_ids:
                    invoice_line_ids.append((0, 0, {
                        'name': line.name,
                        'employee_id': record.employee_id.id,
                        'price_unit': line.amount,
                        'quantity': 1,
                        'service_enquiry_id': record.id
                    }))
                # Create draft.account.move record
                self.env['draft.account.move'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id': record.client_id.parent_id.id if record.client_id.parent_id else False,
                    'service_enquiry_id': record.id,
                    'employee_id': record.employee_id.id,
                    'move_type': 'service_ticket',
                    'invoice_line_ids': invoice_line_ids,
                })
        return result
