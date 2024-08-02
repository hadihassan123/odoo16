
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from pytz import UTC


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    client_name = fields.Char('Client Name',required=True)
    details = fields.Text('Details',required=True)
    work_date = fields.Date('Date of Work',required=True)
    date_of_work_done = fields.Date('Date of Work done')
    your_new_field = fields.Char(string='test')

    work_day = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string='Day of Work', compute='_compute_work_day', store=True)
    create_date = fields.Date(string="Date", tracking=True, default=datetime.today())
    # extra_hours_duration = fields.Float(
    #     string='Duration (Hours)',
    #     compute='_compute_extra_hours_duration',
    #     store=True,
    #     help="Duration of extra hours in decimal format"
    # )
    holiday_status_id = fields.Many2one(
        'hr.leave.type',
        string='Leave Type',
        required=True,
        domain=[('name', '!=', 'Extra Hours')],
        help="Duration of extra hours in decimal format"
    )


    # request_unit_hours = fields.Boolean(default=True)

    @api.model
    def _get_holiday_status_domain(self):
        domain = []  # Start with an empty domain
        extra_hours_type = self.env.ref('hr_holidays_attendance.holiday_status_extra_hours', raise_if_not_found=False)
        if extra_hours_type:
            domain.append(('id', '!=', extra_hours_type.id))

        return domain

    holiday_status_id = fields.Many2one(
        'hr.leave.type',
        domain=_get_holiday_status_domain,
    )

    def _default_request_unit_hours(self):
        if self.holiday_status_id.id:
            return self.holiday_status_id.request_unit == 'hour'
        return False

    request_unit_hours = fields.Boolean(
        "Custom Hours",
        default=_default_request_unit_hours,
        help="If True, the system will allow to request leave in hour"
    )

    # @api.onchange('holiday_status_id')
    # def onchange_holiday_status_id(self):
    #     if self.holiday_status_id.request_unit == 'hour':
    #         self.request_unit_hours = True
    #     else:
    #         self.request_unit_hours = False

    @api.depends('work_date')
    def _compute_work_day(self):
        for record in self:
            if record.work_date:
                record.work_day = record.work_date.strftime('%A').lower()
            else:
                record.work_day = False

    @api.constrains('work_date')
    def _check_work_date(self):
        for record in self:
            compensatory_type = self.env['hr.leave.type'].search([('name', '=', 'Compensatory Days')], limit=1)
            # if record.work_date:
            if (record.holiday_status_id == compensatory_type and record.work_date):
                today = fields.Date.today()
                three_months_ago = today - timedelta(days=90)  # Approximately 3 months

                if record.work_date <= three_months_ago:
                    raise UserError("Work date cannot be more than 3 months from today.")

                calendar = record.employee_id.resource_calendar_id

                # Convert date to datetime
                work_date_start = fields.Datetime.to_datetime(record.work_date)
                work_date_end = work_date_start.replace(hour=23, minute=59, second=59)

                # Ensure datetimes are UTC
                work_date_start = work_date_start.replace(tzinfo=UTC)
                work_date_end = work_date_end.replace(tzinfo=UTC)

                # Check if it's a working day
                working_hours = calendar.get_work_hours_count(
                    work_date_start,
                    work_date_end,
                    compute_leaves=True,
                    domain=[('time_type', '=', 'leave')]
                )
                is_working_day = working_hours > 0

                # Check if it's a public holiday
                public_holidays = self.env['resource.calendar.leaves'].search([
                    ('date_from', '<=', work_date_end),
                    ('date_to', '>=', work_date_start),
                    ('resource_id', '=', False)  # This assumes global holidays
                ])

                is_public_holiday = bool(public_holidays)

                if is_working_day and not is_public_holiday:
                    raise UserError(
                        "Compensatory leave can only be claimed for work done on non-working days or public holidays.")

    @api.constrains('request_date_from', 'create_date', 'holiday_status_id')
    def _check_request_date(self):
        for record in self:
            # Check if the leave type is 'compensatory days'
            compensatory_type = self.env['hr.leave.type'].search([('name', '=',  'Compensatory Days')], limit=1)
            if (record.holiday_status_id == compensatory_type and
                    record.request_date_from and record.create_date):

                application_date = fields.Date.from_string(record.create_date)
                min_request_date = application_date + timedelta(days=7)

                if record.request_date_from < min_request_date:
                    raise UserError(
                        "For compensatory days, the requested leave date must be at least 7 days after the date of application.")
    # @api.constrains('request_date_from', 'create_date')
    # def _check_request_date(self):
    #     for record in self:
    #         if record.request_date_from and record.create_date:
    #             application_date = fields.Date.from_string(record.create_date)
    #             min_request_date = application_date + timedelta(days=7)
    #             if record.request_date_from < min_request_date:
    #                 raise UserError("The requested leave date must be at least 7 days after the date of application.")

    @api.onchange('work_date', 'request_date_from')
    def _onchange_dates(self):
        if self.work_date:
            today = fields.Date.today()
            three_months_ago = today - timedelta(days=90)  # 3 months before today

            if self.work_date <= three_months_ago:
                return {'warning': {
                    'title': "Invalid Work Date",
                    'message': "Compensatory off is only valid for work done within the last 3 months."
                }}

            try:
                self._check_work_date()
            except UserError as e:
                return {'warning': {'title': "Invalid Work Date", 'message': str(e)}}

        if self.request_date_from and self.create_date:
            application_date = fields.Date.from_string(self.create_date)
            min_request_date = application_date + timedelta(days=7)
            if self.request_date_from < min_request_date:
                return
                # {'warning': {
                #     'title': "Invalid Request Date",
                #     'message': "The requested leave date must be at least 7 days after the date of application."
                # }}

    # @api.depends('request_hour_from', 'request_hour_to')
    # def _compute_extra_hours_duration(self):
    #     for leave in self:
    #         if leave.request_hour_from and leave.request_hour_to:
    #             try:
    #                 time_from = float(leave.request_hour_from)
    #                 time_to = float(leave.request_hour_to)
    #                 duration = time_to - time_from
    #                 leave.extra_hours_duration = max(0, duration)  # Ensure non-negative duration
    #             except ValueError:
    #                 leave.extra_hours_duration = 0
    #         else:
    #             leave.extra_hours_duration = 0
    #
    # @api.onchange('holiday_status_id', 'request_hour_from', 'request_hour_to', 'date_of_work_done')
    # def _onchange_check_extra_hours(self):
    #     if self.holiday_status_id.name == 'Extra Hours':
    #         if self.request_hour_from and self.request_hour_to and self.date_of_work_done:
    #             try:
    #                 time_from = float(self.request_hour_from)
    #                 time_to = float(self.request_hour_to)
    #                 duration = time_to - time_from
    #                 # Check duration
    #                 if duration < 2:
    #                     return {'warning': {
    #                         'title': "Invalid Extra Hours",
    #                         'message': "Extra hours must be at least 2 hours."
    #                     }}
    #
    #                 # Check if outside office hours
    #                 if not (time_from <= 9 or time_from >= 17) or not (time_to <= 9 or time_to >= 17):
    #                     return {'warning': {
    #                         'title': "Invalid Extra Hours",
    #                         'message': "Extra hours must be outside office hours (before 9:00 AM or after 5:00 PM)."
    #                     }}
    #
    #                 # Check if claim is within 2 working days
    #                 today = fields.Date.today()
    #                 work_done_date = self.date_of_work_done
    #                 days_difference = self._get_working_days_between(work_done_date, today)
    #                 if days_difference > 2:
    #                     return {'warning': {
    #                         'title': "Late Claim",
    #                         'message': "Extra hours claim must be made within 2 working days from the date of work done."
    #                     }}
    #
    #             except ValueError:
    #                 return {'warning': {
    #                     'title': "Invalid Time Format",
    #                     'message': "Please enter valid time values."
    #                 }}
    #
    #         # elif self.request_hour_from or self.request_hour_to:
    #         #     return {'warning': {
    #         #         'title': "Incomplete Time Entry",
    #         #         'message': "Please specify both start and end times for Extra Hours."
    #         #     }}
    #
    # @api.constrains('holiday_status_id', 'request_hour_from', 'request_hour_to', 'date_of_work_done')
    # def _check_extra_hours(self):
    #     for record in self:
    #         if record.holiday_status_id.name == 'Extra Hours':
    #             if record.request_hour_from and record.request_hour_to and record.date_of_work_done:
    #                 try:
    #                     time_from = float(record.request_hour_from)
    #                     time_to = float(record.request_hour_to)
    #                     duration = time_to - time_from
    #
    #                     if duration < 2:
    #                         raise ValidationError("Extra hours must be at least 2 hours.")
    #
    #                     if not (time_from <= 9 or time_from >= 17) or not (time_to <= 9 or time_to >= 17):
    #                         raise ValidationError(
    #                             "Extra hours must be outside office hours (before 9:00 AM or after 5:00 PM).")
    #
    #                     today = fields.Date.today()
    #                     work_done_date = record.date_of_work_done
    #                     days_difference = self._get_working_days_between(work_done_date, today)
    #                     if days_difference > 2:
    #                         raise UserError(
    #                             "Extra hours claim must be made within 2 working days from the date of work done.")
    #
    #                 except ValueError:
    #                     raise UserError("Please enter valid time values.")
    #
    # def _get_working_days_between(self, start_date, end_date):
    #     """Calculate the number of working days between two dates."""
    #     current_date = start_date
    #     working_days = 0
    #     while current_date <= end_date:
    #         if current_date.weekday() < 5:  # Monday = 0, Friday = 4
    #             working_days += 1
    #         current_date += timedelta(days=1)
    #     return working_days

#
# class HrLeaveType(models.Model):
#     _inherit = 'hr.leave.type'
#
#     is_extra_hours = fields.Boolean(compute='_compute_is_extra_hours', store=True)
#
#     @api.depends('id')
#     def _compute_is_extra_hours(self):
#         extra_hours_type = self.env.ref('hr_holidays_attendance.holiday_status_extra_hours', False)
#         for leave_type in self:
#             leave_type.is_extra_hours = leave_type.id == extra_hours_type.id if extra_hours_type else False