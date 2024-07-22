from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import base64
from odoo.exceptions import UserError

class ScheduledAction(models.Model):
    _name = 'scheduled.action.model'
    _description = 'Scheduled Action'

    def is_public_holiday(self):
        today = datetime.today().date()
        # Query public holidays from the time off model
        leaves_records = self.env['resource.calendar.leaves'].search([])
        # Check if today matches any public holiday
        for leave_record in leaves_records:
            date_from = leave_record.date_from
            date_to = leave_record.date_to
            if date_from.date() <= today <= date_to.date():
                return True
        return False

    @api.model
    def send_ticket_escalation_emails(self):
        current_year = datetime.now().year
        public_holidays = self.is_public_holiday()
        tickets = self.env['maintenance.customers'].search([('state', '=', 'open'),
                                                            ('sla', 'in', ['critical', 'moderate', 'minimal'])])
        for ticket in tickets:
            ticket.send_ticket_escalation_emails()

