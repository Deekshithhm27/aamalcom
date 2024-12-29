import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model_create_multi
    def create(self, vals_list):

        _logger.info("\n Custom log: Entering 'create' method in mail.followers.")
        # Get the group(s) you want to restrict
        restricted_group = self.env.ref('visa_process.group_service_request_client_spoc')

        # Filter out the followers that belong to the restricted group
        filtered_vals_list = []
        for vals in vals_list:
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            user = partner.user_ids[:1]

            if not user or restricted_group not in user.groups_id:
                filtered_vals_list.append(vals)

        # Create followers only for the non-restricted users
        res = super(Followers, self).create(filtered_vals_list)
        return res
