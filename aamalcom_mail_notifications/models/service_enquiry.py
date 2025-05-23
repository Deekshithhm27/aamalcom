from odoo import models, fields

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    message_history_ids = fields.One2many(
        'message.history',
        'service_enquiry_id',
        string="Message History"
    )
    message_text = fields.Text(string="Message")

    #oe_chatter is internal-only.So this medium for client and PM communication.
    def send_message(self):
        for record in self:
            if record.message_text:
                message = record.message_text
                message_history_vals = {
                    'service_enquiry_id': record.id,
                    'message': message,
                    'sender': self.env.user.id,
                }
                self.env['message.history'].sudo().create(message_history_vals)
                # Clear the message_text field after sending the message
                record.message_text = False

                # client sent mail to pm else sent to client
                if self.env.user.partner_id.id == record.client_id.id:
                    template = self.env.ref('aamalcom_mail_notifications.mail_template_service_enquiry_client_sent')
                    template.with_context(custom_message=message).send_mail(record.id, force_send=True)
                else:
                    template = self.env.ref('aamalcom_mail_notifications.mail_template_service_enquiry_internal_sent')
                    template.with_context(custom_message=message).send_mail(record.id, force_send=True)