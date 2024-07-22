# Import necessary modules
from odoo import models, _
from odoo.exceptions import UserError

class ServerActionExportRelatedAssets(models.Model):
    _name = 'ir.actions.server'
    _inherit = 'ir.actions.server'

    def run(self, action, eval_context=None):
        # Ensure the 'action' parameter is included in the method signature
        if not action:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('No action specified.'),
                    'type': 'danger',
                },
            }

        # Your logic here
        # Ensure you have the necessary code to handle the 'action' parameter

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Server action executed successfully.'),
                'type': 'success',
            },
        }