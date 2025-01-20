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

                # if client sent mail to pm else sent to client
                if self.env.user.partner_id.id == record.client_id.id:
                    mail_values = {
                        'subject': f'Service Enquiry Communication - {record.name}',
                        'email_from': self.env.user.user_id.partner_id.email,
                        'email_to': record.client_id.company_spoc_id.user_id.email,
                        'body_html': f"""
                                <div>
                                    <p>Dear Sir,</p>
                                    <p>You have received a message from {self.env.user.name}.:</p>
                                    <p>"{message}"</p>
                                </div>
                                <div>Thank You</div>
                            """,
                    }
                    mail_id = self.env['mail.mail'].sudo().create(mail_values)
                    mail_id.sudo().send()
                else:
                    mail_values = {
                        'subject': f'Service Enquiry Communication - {record.name}',
                        'email_from': self.env.user.user_id.partner_id.email,
                        'email_to': record.client_id.email,
                        'body_html': f"""
                                <div>
                                    <p>Dear Sir,</p>
                                    <p>You have received a message from {self.env.user.name}.:</p>
                                    <p>"{message}"</p>
                                </div>
                                <div>Thank You</div>
                            """,
                    }
                    mail_id = self.env['mail.mail'].sudo().create(mail_values)
                    mail_id.sudo().send()
