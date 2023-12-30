from odoo import api, fields, models, _
import ast

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_spoc = fields.Boolean(string="Is Spoc",default=True)

    draft_count = fields.Integer(string='Draft Count', compute='_compute_sourcing_counts')
    open_count = fields.Integer(string='Open Count', compute='_compute_sourcing_counts')
    close_count = fields.Integer(string='Close Count', compute='_compute_sourcing_counts')

    color = fields.Integer('Color')
    code = fields.Selection([('spoc','Spoc'), ('employee', 'Employee')], 'Type of Code',default='spoc')

    count_service_enquiry_draft = fields.Integer(compute='_compute_service_enquiry_count')
    count_service_enquiry_submitted = fields.Integer(compute='_compute_service_enquiry_count')
    count_service_enquiry_done = fields.Integer(compute='_compute_service_enquiry_count')

    
    @api.onchange('is_spoc')
    def _update_code(self):
        if not self.is_spoc:
            self.update({'code':'employee'})
        else:
            self.update({'code':'spoc'})

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        # client_id = self.env['res.partner'].search([('enable_wo','=',True)])

        context = {
            'search_default_approver_id': [self.id],
            'default_approver_id': self.id,
            'default_company_id': self.company_id.id,
        }

        action_context = ast.literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action


    def _compute_service_enquiry_count(self):
        # TDE TODO count can be done using previous two
        domains = {
            'count_service_enquiry_draft': [('state', '=', 'draft')],
            'count_service_enquiry_submitted': [('state', '=', 'submitted')],
            'count_service_enquiry_done': [('state', '=','done')],
        }
        for field in domains:
            data = self.env['service.enquiry'].read_group(domains[field] +
                [('approver_id', 'in', self.ids)],
                ['approver_id'], ['approver_id'])
            count = {
                x['approver_id'][0]: x['approver_id_count']
                for x in data if x['approver_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)


    def get_action_service_enquiry_tree_draft(self):
        return self._get_action('overview_dashboard.action_service_enquiry_tree_draft')

    def get_action_service_enquiry_tree_submited(self):
        return self._get_action('overview_dashboard.action_service_enquiry_tree_submitted')
    

    def get_action_partner_tree_done(self):
        return self._get_action('overview_dashboard.action_service_enquiry_tree_done')
