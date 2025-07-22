import base64
from io import BytesIO
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter

from odoo import models, fields, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_insurance_merged_pdf = fields.Binary(
    string="Merged Invoice + Insurance PDF"
    )
    merged_pdf_filename = fields.Char(
        string="Merged PDF Filename"
    )
 
    # reports
    def action_invoice_tax_report(self, type):
        self.ensure_one()
        if type == 'tax_invoice':
            template = self.env.ref('aamalcom_accounting_reporting.email_template_edi_invoice_tax_etir', raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            active_ids=[self.id],
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def action_save_merged_insurance_pdf(self):
        for move in self:
            # get both report actions
            invoice_report = self.env.ref("aamalcom_accounting_reporting.action_report_tax_invoice")
            insurance_report = self.env.ref("aamalcom_accounting_reporting.action_report_insurance_invoice")

            # render QWeb PDFs
            invoice_pdf, _ = invoice_report._render_qweb_pdf(move.ids)
            insurance_pdf, _ = insurance_report._render_qweb_pdf(move.ids)

            # merge: start with invoice
            merger = PdfFileMerger()
            merger.append(BytesIO(invoice_pdf))

            # rotate insurance
            insurance_reader = PdfFileReader(BytesIO(insurance_pdf))
            insurance_writer = PdfFileWriter()
            for i in range(insurance_reader.getNumPages()):
                page = insurance_reader.getPage(i)
                page.rotateClockwise(90)   # rotate to portrait style
                insurance_writer.addPage(page)
            rotated_buffer = BytesIO()
            insurance_writer.write(rotated_buffer)
            rotated_buffer.seek(0)

            merger.append(rotated_buffer)

            # if proof_of_document is uploaded, merge it too
            if move.proof_of_document:
                proof_buffer = BytesIO(base64.b64decode(move.proof_of_document))
                proof_reader = PdfFileReader(proof_buffer)
                proof_writer = PdfFileWriter()
                for i in range(proof_reader.getNumPages()):
                    page = proof_reader.getPage(i)
                    # optionally rotate if needed
                    # page.rotateClockwise(0)
                    proof_writer.addPage(page)
                final_proof_buffer = BytesIO()
                proof_writer.write(final_proof_buffer)
                final_proof_buffer.seek(0)

                merger.append(final_proof_buffer)


            # final
            final_buffer = BytesIO()
            merger.write(final_buffer)
            merger.close()

            move.invoice_insurance_merged_pdf = base64.b64encode(final_buffer.getvalue())
            move.merged_pdf_filename = f"{move.name or 'invoice'}_merged.pdf"

        return True

    def action_post(self):
        if move.invoice_type == 'insurance':
            self.action_save_merged_insurance_pdf()
        return super(AccountMove, self).action_post()