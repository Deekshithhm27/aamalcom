📌 Document & PDF to Image Support in Odoo Reports

This module adds support for displaying uploaded PDFs (converted to images) and images inside QWeb reports (e.g., Invoices linked to service.enquiry).

🔧 Dependencies

We use:

pdf2image
 → Python library to convert PDF pages to images.

poppler-utils
 → required backend for pdf2image.

⚡ Installation Steps

Run the following commands on your Odoo server:
# 1. Install pdf2image (user-level installation since system site-packages not writable)
pip3 install --user pdf2image

# 2. Install poppler-utils (already available on Ubuntu repositories)
sudo apt-get install poppler-utils

✅ Verify installation:
# Check pdf2image installed
python3 -m pip show pdf2image

# Check poppler installed
pdftoppm -h

📝 Notes

pdf2image requires poppler-utils to be installed on the system (pdftoppm binary must be available).

In our module (service_enquiry.py), we use:

from pdf2image import convert_from_bytes


to convert the first page of a PDF to PNG and return it as base64 so it can be directly rendered in QWeb <img> tags.
3. No changes required in account.move, everything is handled inside the service.enquiry model.