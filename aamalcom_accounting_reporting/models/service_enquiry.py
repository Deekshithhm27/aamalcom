from odoo import models
from io import BytesIO
import base64
from pdf2image import convert_from_bytes

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    def get_displayable_image(self, binary_field):
        """
        Returns base64-encoded PNG string for display in QWeb <img>.
        If input is PDF -> convert first page to PNG.
        If input is already image -> return as base64 string.
        """
        if not binary_field:
            return False

        data_bytes = base64.b64decode(binary_field)

        if data_bytes[:4] == b'%PDF':
            # Convert first page of PDF to image
            images = convert_from_bytes(data_bytes, dpi=150)
            img_byte_arr = BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        else:
            # Already an image, ensure return is string
            return binary_field.decode("utf-8") if isinstance(binary_field, bytes) else binary_field
