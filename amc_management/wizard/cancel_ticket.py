from odoo import api,fields,models
from datetime import datetime
import base64
import datetime
import csv
import binascii
import logging

_logger = logging.getLogger(__name__)


class CancelTicketWizard(models.TransientModel):
    _name = "cancel.ticket.wizard"
    _description = "cancel ticket wizard"

    remarks = fields.Char(string = "remarks")
    amc_customer_id = fields.Many2one('amc.customers',string='amc')
    file_data = fields.Binary(string="CSV File")
    state = fields.Selection([('cancel', 'cancelled')])

    def action_cancel(self):
        if self.file_data:
            file_content = base64.b64decode(self.file_data)
            decoded_content = file_content.decode('utf-8')
            csv_data = csv.reader(decoded_content.splitlines())
            date_format = "%m/%d/%Y"

            # Skip the header row
            next(csv_data, None)

            for row in csv_data:
                wty_start_date = datetime.datetime.strptime(row[3], date_format).date()
                amc_customer_id = self.env['amc.customers'].search([('name', '=', row[5])], limit=1)
                asset_values = {
                    'asset_name': row[0],
                    'asset_tag': row[1],
                    'serial_no': row[2],
                    'wty_start': wty_start_date,
                    'vendor': row[4],
                    'asset_upload_id': amc_customer_id.id if amc_customer_id else False,

                }

                try:
                    create_asset = self.env['upload.asset'].create(asset_values)
                    _logger.info("Asset Values: %s", asset_values)
                    _logger.info("Created asset with ID: %s", create_asset.id)
                    print("Asset Values:", asset_values)
                    print("Created asset with ID:", create_asset.id)
                except Exception as e:
                    print(f"Error creating asset: {e}")
                    continue

            # Commit the changes
            self.env.cr.commit()

        return {'type': 'ir.actions.act_window_close'}

    def cancel_ticket(self):
        # Additional logic for canceling ticket if needed
        pass