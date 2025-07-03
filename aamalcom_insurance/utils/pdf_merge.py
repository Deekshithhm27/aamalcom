from PyPDF2 import PdfFileMerger
from io import BytesIO

def merge_invoice_and_insurance(invoice):
    # Render the portrait invoice
    report_invoice = invoice.env.ref('aamalcom_accounting.report_tax_invoice')
    invoice_pdf, _ = report_invoice._render_qweb_pdf([invoice.id])

    # Render the landscape insurance report
    insurance_report = invoice.env.ref('aamalcom_insurance.partial_insurance_invoice_landscape')
    insurance_pdf, _ = insurance_report._render_qweb_pdf([invoice.id])

    # Merge using PdfFileMerger (compatible with PyPDF2 1.26.0)
    merger = PdfFileMerger()
    merger.append(BytesIO(invoice_pdf))
    merger.append(BytesIO(insurance_pdf))

    merged_buffer = BytesIO()
    merger.write(merged_buffer)
    merger.close()

    return merged_buffer.getvalue()
