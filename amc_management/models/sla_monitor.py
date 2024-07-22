from datetime import timedelta, datetime

from odoo import api, fields, models




class SLAMonitor(models.Model):
    _name = 'sla.monitor'
    _description = 'SLA Monitor'
    _inherit = 'mail.thread'
    _rec_name = "ticket_id"

    partner_id = fields.Many2one('res.partner', string='Partner')
    ticket_id = fields.Many2one('maintenance.customers', string='Ticket',)
    ref = fields.Char(string='ticket number',related='ticket_id.ref')
    old_state = fields.Selection([
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('work in progress', 'Work in Progress'),
        ('waiting for customer', 'Waiting for Customer'),
        ('waiting for vendor', 'Waiting for Vendor'),
        ('resolved', 'Resolved'),
        ('cancel','Cancel'),
        ('done', 'Done'),
        ('reopen','reopen')
    ], string='Old State')
    new_state = fields.Selection([
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('work in progress', 'Work in Progress'),
        ('waiting for customer', 'Waiting for Customer'),
        ('waiting for vendor', 'Waiting for Vendor'),
        ('resolved', 'Resolved'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
        ('reopen', 'Reopen')
    ], string='New State',track_visibility='onchange')
    timestamp = fields.Datetime(string='Timestamp')
    sla_monitor_id = fields.Many2one('maintenance.customers',string='sla monitor')
    duration = fields.Char(string='Total Duration (Hours)', compute='_compute_duration',store=True)
    open_assigned_duration = fields.Float(string='Open to Assigned Duration')
    assigned_work_in_progress_duration = fields.Float(string='Assigned to Work In Progress Duration')
    work_in_progress_waiting_for_customer_duration = fields.Float(string='Work In Progress to Waiting For Customer Duration')
    work_in_progress_waiting_for_vendor_duration = fields.Float(string='Work In Progress to Waiting For Vendor')
    work_in_progress_resolved = fields.Float(string='Work In progress to resolved')
    calendar_id = fields.Many2one('resource.calendar', string='Calendar')
    leave_id = fields.Many2one('hr.leave', string='Leave')
    leave_type_id = fields.Many2one('hr.leave.type', string='Leave Type')
    calendar_leave_id = fields.Many2one('resource.calendar.leaves', string='Calendar Leave')
    time_from = fields.Char(string='Time From', compute='_compute_time_from', store=True)
    is_reopened = fields.Boolean(string='Is Reopened', default=False)


    @api.depends('calendar_leave_id.date_from')
    def _compute_time_from(self):
        for record in self:
            if record.calendar_leave_id.date_from:
                datetime_value = fields.Datetime.from_string(record.calendar_leave_id.date_from)
                time_value = datetime_value.strftime('%H:%M')  # Format time as HH:MM
                record.time_from = time_value
            else:
                record.time_from = ''
     # 5:00 PM

    # @api.depends('ticket_id')
    # def _compute_duration(self):
    #     for record in self:
    #         total_duration = 0.0
    #         current_state = None
    #         state_timestamp = None
    #         open_timestamp = None
    #
    #         # Get all SLA monitors related to the ticket, ordered by timestamp
    #         sla_monitors = self.env['sla.monitor'].search([('ref', '=', record.ref)], order='timestamp asc')
    #
    #         for monitor in sla_monitors:
    #             state = monitor.new_state
    #             timestamp = monitor.timestamp
    #
    #             print(f"Processing state '{state}' at timestamp '{timestamp}'")
    #
    #             if state == 'open':
    #                 print("Ticket is now in 'open' state.")
    #                 open_timestamp = timestamp
    #                 state_timestamp = timestamp
    #                 current_state = state
    #             elif state == 'resolved':
    #                 print("Ticket is now in 'resolved' state.")
    #                 if current_state == 'open':
    #                     # Calculate duration from 'open' to 'resolved'
    #                     total_duration += (timestamp - open_timestamp).total_seconds()
    #                     print(
    #                         f"Duration from 'open' to 'resolved': {(timestamp - open_timestamp).total_seconds()} seconds")
    #                 elif current_state in ['waiting for vendor', 'waiting for customer']:
    #                     # If resolved after waiting state, add duration since last state change (open)
    #                     total_duration += (timestamp - state_timestamp).total_seconds()
    #                     print(
    #                         f"Duration since last state change ({current_state}): {(timestamp - state_timestamp).total_seconds()} seconds")
    #
    #                 # Reset state tracking
    #                 current_state = state
    #                 state_timestamp = timestamp
    #                 open_timestamp = None
    #             elif state in ['waiting for vendor', 'waiting for customer']:
    #                 print(f"Ticket is now in '{state}' state.")
    #                 if current_state == 'open':
    #                     # If directly goes into waiting state after open, reset open timestamp
    #                     open_timestamp = None
    #
    #                 # Set state timestamp for waiting states but don't add duration to total
    #                 state_timestamp = timestamp
    #                 current_state = state
    #             else:
    #                 # Handle transitions back to work in progress or other states
    #                 print(f"Ticket is now in '{state}' state.")
    #                 current_state = state
    #                 state_timestamp = timestamp
    #
    #         # Set the calculated total duration as the record's duration
    #         record.duration = total_duration
    #         print(f"Total duration calculated: {total_duration} seconds")
    @api.depends('ticket_id')
    def _compute_duration(self):
        for record in self:
            duration = 0.0
            state_transitions = {}
            sla_monitors = self.env['sla.monitor'].search([('ref', '=', record.ref)])
            print("SLA Monitors:", sla_monitors)
            for monitor in sla_monitors.sorted(key=lambda r: r.timestamp):
                print("Monitor:", monitor)
                if monitor.new_state == 'open':
                    if monitor.new_state not in state_transitions:
                        state_transitions[monitor.new_state] = []
                    state_transitions[monitor.new_state].append(monitor.timestamp)

            print("State Transitions:", state_transitions)

            for state, timestamps in state_transitions.items():
                print("State:", state)
                print("Timestamps:", timestamps)
                for i in range(0, len(timestamps), 2):
                    start_time = timestamps[i]
                    end_time = timestamps[i + 1] if i + 1 < len(timestamps) else fields.Datetime.now()
                    # Check if the state is "waiting for vendor" or "waiting for customer"
                    if state in ['waiting for vendor','waiting for customer']:
                        # If yes, don't include the duration in the total duration
                        continue

                    duration_seconds = (end_time - start_time)
                    duration = duration_seconds
                    print("Start Time:", start_time)
                    print("End Time:", end_time)
                    print("Duration Seconds:", duration_seconds)

            record.duration = duration
            print("Total Duration:", duration)

    @api.depends('ticket_id')
    def _compute_state_durations(self):
        for record in self:
            total_duration_seconds = 0.0
            state_durations = {}
            sla_monitors = record.ticket_id.sla_monitor_ids.sorted(key=lambda r: r.timestamp)
            print(f"Processing record: {record}")

            previous_state = None
            previous_timestamp = None
            current_day_of_week = datetime.now().weekday()
            ticket_reopened = False

            # Fetch office hours for the current day of the week
            office_hours_attendances = self.env['resource.calendar.attendance'].search([
                ('dayofweek', '=', current_day_of_week),
            ])
            office_hours = []
            if office_hours_attendances:
                for attendance in office_hours_attendances:
                    start_hour = attendance.hour_from
                    end_hour = attendance.hour_to

                    # Split the time range into two parts if it spans the lunch break
                    if start_hour < 12 and end_hour > 13:
                        office_hours.append((start_hour, 12.0))  # First part before lunch break
                        office_hours.append((13.0, end_hour))  # Second part after lunch break
                    else:
                        office_hours.append((start_hour, end_hour))

                print(f"Office Hours: {office_hours}")
            else:
                # Default office hours (e.g., 9 AM to 12 PM, and 1 PM to 5 PM) if no specific attendances are found
                office_hours = [(5.0, 12.0), (13.0, 17.0)]
                print(f"Office Hours: {office_hours}")

            # Fetch public holidays from resource.calendar.leaves
            public_holidays = record.env['resource.calendar.leaves'].search([]).mapped('date_from')
            print(f"Public Holidays: {public_holidays}")

            for monitor in sla_monitors:
                current_state = monitor.new_state
                current_timestamp = fields.Datetime.from_string(monitor.timestamp)

                # if current_state == 'reopen':
                #     record.is_reopened = True
                #     ticket_reopened = True
                #     previous_state = 'reopen'
                #     previous_timestamp = current_timestamp
                #     total_duration_seconds = 0.0
                #     state_durations = {}
                if current_state == 'reopen':
                    record.is_reopened = True
                    ticket_reopened = True
                    previous_state = None
                    previous_timestamp = None
                    total_duration_seconds = 0.0
                    state_durations = {}

                if previous_state and previous_timestamp:
                    transition_key = f"{previous_state}->{current_state}"
                    state_durations.setdefault(transition_key, timedelta(seconds=0))

                    # Calculate time spent between state transitions
                    time_spent = current_timestamp - previous_timestamp

                    # Check if the previous state was a waiting state
                    if previous_state in ['waiting for vendor', 'waiting for customer']:
                        print("waiting state")
                        # Skip counting the time spent if transitioning from a waiting state
                        pass
                    else:
                        print("not waiting state")

                        # Calculate the remaining duration from the previous day's office hours
                        remaining_duration = timedelta(seconds=0)
                        if previous_timestamp.date() != current_timestamp.date():
                            previous_day_of_week = previous_timestamp.weekday()
                            previous_office_hours_attendances = record.env['resource.calendar.attendance'].search([
                                ('dayofweek', '=', previous_day_of_week),
                            ])
                            if previous_office_hours_attendances:
                                previous_office_hours = []
                                for attendance in previous_office_hours_attendances:
                                    start_hour = attendance.hour_from
                                    end_hour = attendance.hour_to

                                    # Split the time range into two parts if it spans the lunch break
                                    if start_hour < 12 and end_hour > 13:
                                        previous_office_hours.append((start_hour, 12.0))
                                        previous_office_hours.append((13.0, end_hour))
                                    else:
                                        previous_office_hours.append((start_hour, end_hour))

                                previous_day_end_time = datetime.combine(previous_timestamp.date(), datetime.min.time())
                                for start_hour, end_hour in previous_office_hours:
                                    previous_day_end_time += timedelta(hours=end_hour)
                                    if previous_timestamp < previous_day_end_time:
                                        remaining_duration = previous_day_end_time - previous_timestamp
                                        break

                        # Check if the current timestamp falls within office hours and is not on a public holiday
                        within_office_hours = any(start_hour <= current_timestamp.hour < end_hour and
                                                  current_timestamp.date() not in public_holidays
                                                  for start_hour, end_hour in office_hours)
                        if within_office_hours:
                            print(" within office hours")
                            state_durations[transition_key] += time_spent + remaining_duration
                            print(f"Time spent in {transition_key}: {time_spent} + {remaining_duration}")
                            if not ticket_reopened or (ticket_reopened and current_state != 'resolved'):
                                total_duration_seconds += (time_spent + remaining_duration).total_seconds()


                        # Check if the current state is 'resolved' and the ticket was reopened
                        elif current_state == 'resolved' and ticket_reopened:
                            # Check if the previous timestamp falls within office hours and is not on a public holiday
                            within_office_hours = any(start_hour <= previous_timestamp.hour < end_hour and
                                                      previous_timestamp.date() not in public_holidays
                                                      for start_hour, end_hour in office_hours)
                            if within_office_hours:
                                print(" within office hours")
                                state_durations[transition_key] = time_spent
                                print(f"Time spent in {transition_key}: {time_spent}")
                                total_duration_seconds += time_spent.total_seconds()
                        # Check if the current state is a waiting state
                        # elif current_state in ['waiting for vendor', 'waiting for customer', 'resolved']:
                        #     # Check if the previous state was 'work in progress'
                        #     if previous_state == 'work in progress':
                        #         # Check if the previous timestamp falls within office hours and is not on a public holiday
                        #         within_office_hours = any(start_hour <= previous_timestamp.hour < end_hour and
                        #                                   previous_timestamp.date() not in public_holidays
                        #                                   for start_hour, end_hour in office_hours)
                        #         if within_office_hours:
                        #             print(" within office hours")
                        #             transition_key = f"{previous_state}->{current_state}"
                        #             state_durations[transition_key] = time_spent
                        #             print(f"Time spent in {transition_key}: {time_spent}")
                        #             if not ticket_reopened:
                        #                 total_duration_seconds += time_spent.total_seconds()
                        elif current_state in ['waiting for vendor', 'waiting for customer']:
                            # Check if the previous state was 'work in progress'
                            if previous_state == 'work in progress':
                                # Check if the previous timestamp falls within office hours and is not on a public holiday
                                within_office_hours = any(start_hour <= previous_timestamp.hour < end_hour and
                                                          previous_timestamp.date() not in public_holidays
                                                          for start_hour, end_hour in office_hours)
                                if within_office_hours:
                                    print(" within office hours")
                                    state_durations[transition_key] += time_spent
                                    print(f"Time spent in {transition_key}: {time_spent}")
                                    if not ticket_reopened:
                                        total_duration_seconds += time_spent.total_seconds()



                        elif current_state == 'resolved' and previous_state == 'work in progress':

                            # Check if the current timestamp falls within office hours and is not on a public holiday

                            within_office_hours = any(start_hour <= current_timestamp.hour < end_hour and

                                                      current_timestamp.date() not in public_holidays

                                                      for start_hour, end_hour in office_hours)

                            if within_office_hours:

                                print(" within office hours")

                                transition_key = f"{previous_state}->{current_state}"

                                state_durations[transition_key] = time_spent

                                print(f"Time spent in {transition_key}: {time_spent}")

                                if not ticket_reopened:
                                    total_duration_seconds += time_spent.total_seconds()

                # Update previous state and timestamp
                previous_state = current_state
                previous_timestamp = current_timestamp

            # Format total duration as HH:MM:SS
            total_duration = str(timedelta(seconds=total_duration_seconds))

            # Build a formatted string representation of state durations
            # state_durations_str = "\n".join(f"{key}: {str(value)}" for key, value in state_durations.items())
            # print(f"Total Duration for record {record}: {total_duration}")
            # print(f"State Durations for record {record}:\n{state_durations_str}")
            #
            # # Set the formatted total duration and state durations to the record
            # record.total_duration = total_duration
            # record.state_durations = state_durations_str
            if state_durations:
                last_state_transition_key = list(state_durations.keys())[-1]
                state_duration_strings = list(state_durations.values())[-1]
                state_duration_strings_str = str(state_duration_strings)
                state_duration_strings = [state_duration_strings_str]
            else:
                last_state_transition_key = ""
                state_duration_strings_str = ""
                state_duration_strings = []
            # last_state_transition_key = list(state_durations.keys())[-1]
            # state_duration_strings = [str(list(state_durations.values())[-1])]

            total_duration = str(timedelta(seconds=total_duration_seconds))

            print(f"Total Duration for record {record}: {total_duration}")
            print(f"State Durations for record {record}:")
            for duration_str in state_duration_strings:
                print(duration_str)

            # Set the formatted total duration and state durations to the record
            record.total_duration = total_duration
            record.state_durations = state_duration_strings_str
            record.key_duration = last_state_transition_key
    # @api.depends('ticket_id')
    # def _compute_state_durations(self):
    #     for record in self:
    #         total_duration_seconds = 0.0
    #         state_durations = {}
    #         sla_monitors = record.ticket_id.sla_monitor_ids.sorted(key=lambda r: r.timestamp)
    #         print(f"Processing record: {record}")
    #
    #         previous_state = None
    #         previous_timestamp = None
    #         current_day_of_week = datetime.now().weekday()
    #
    #         # Fetch office hours for the current day of the week
    #         office_hours_attendances = self.env['resource.calendar.attendance'].search([
    #             ('dayofweek', '=', current_day_of_week),
    #         ])
    #         office_hours = []
    #         if office_hours_attendances:
    #              for attendance in office_hours_attendances:
    #                  start_hour = attendance.hour_from
    #                  end_hour = attendance.hour_to
    #
    #                  # Split the time range into two parts if it spans the lunch break
    #                  if start_hour < 12 and end_hour > 13:
    #                      office_hours.append((start_hour, 12.0))  # First part before lunch break
    #                      office_hours.append((13.0, end_hour))  # Second part after lunch break
    #                  else:
    #                      office_hours.append((start_hour, end_hour))
    #
    #              print(f"Office Hours: {office_hours}")
    #         else:
    #         # Default office hours (e.g., 9 AM to 12 PM, and 1 PM to 5 PM) if no specific attendances are found
    #             office_hours = [(5.0, 12.0), (13.0, 17.0)]
    #             print(f"Office Hours: {office_hours}")
    #
    #         # Fetch public holidays from resource.calendar.leaves
    #         public_holidays = record.env['resource.calendar.leaves'].search([]).mapped('date_from')
    #         print(f"Public Holidays: {public_holidays}")
    #
    #         for monitor in sla_monitors:
    #             current_state = monitor.new_state
    #             current_timestamp = fields.Datetime.from_string(monitor.timestamp)
    #
    #             if previous_state and previous_timestamp:
    #                 transition_key = f"{previous_state}->{current_state}"
    #                 state_durations.setdefault(transition_key, timedelta(seconds=0))
    #
    #                 # Calculate time spent between state transitions
    #                 time_spent = current_timestamp - previous_timestamp
    #
    #                 # Check if the previous state was a waiting state
    #                 if previous_state in ['waiting for vendor', 'waiting for customer']:
    #                     print("waiting state")
    #                     # Skip counting the time spent if transitioning from a waiting state
    #                     pass
    #                 else:
    #                     print("not waiting state")
    #
    #                     # Calculate the remaining duration from the previous day's office hours
    #                     remaining_duration = timedelta(seconds=0)
    #                     if previous_timestamp.date() != current_timestamp.date():
    #                         previous_day_of_week = previous_timestamp.weekday()
    #                         previous_office_hours_attendances = record.env['resource.calendar.attendance'].search([
    #                             ('dayofweek', '=', previous_day_of_week),
    #                         ])
    #                         if previous_office_hours_attendances:
    #                             previous_office_hours = []
    #                             for attendance in previous_office_hours_attendances:
    #                                 start_hour = attendance.hour_from
    #                                 end_hour = attendance.hour_to
    #
    #                                 # Split the time range into two parts if it spans the lunch break
    #                                 if start_hour < 12 and end_hour > 13:
    #                                     previous_office_hours.append((start_hour, 12.0))
    #                                     previous_office_hours.append((13.0, end_hour))
    #                                 else:
    #                                     previous_office_hours.append((start_hour, end_hour))
    #
    #                             previous_day_end_time = datetime.combine(previous_timestamp.date(), datetime.min.time())
    #                             for start_hour, end_hour in previous_office_hours:
    #                                 previous_day_end_time += timedelta(hours=end_hour)
    #                                 if previous_timestamp < previous_day_end_time:
    #                                     remaining_duration = previous_day_end_time - previous_timestamp
    #                                     break
    #
    #                     # Check if the current timestamp falls within office hours and is not on a public holiday
    #                     within_office_hours = any(start_hour <= current_timestamp.hour < end_hour and
    #                                               current_timestamp.date() not in public_holidays
    #                                               for start_hour, end_hour in office_hours)
    #                     if within_office_hours:
    #                         print(" within office hours")
    #                         state_durations[transition_key] += time_spent + remaining_duration
    #                         print(f"Time spent in {transition_key}: {time_spent} + {remaining_duration}")
    #                         total_duration_seconds += (time_spent + remaining_duration).total_seconds()
    #
    #                     # Check if the current state is a waiting state
    #                     elif current_state in ['waiting for vendor', 'waiting for customer']:
    #                         # Check if the previous state was 'work in progress'
    #                         if previous_state == 'work in progress':
    #                             # Check if the previous timestamp falls within office hours and is not on a public holiday
    #                             within_office_hours = any(start_hour <= previous_timestamp.hour < end_hour and
    #                                                       previous_timestamp.date() not in public_holidays
    #                                                       for start_hour, end_hour in office_hours)
    #                             if within_office_hours:
    #                                 print(" within office hours")
    #                                 state_durations[transition_key] += time_spent
    #                                 print(f"Time spent in {transition_key}: {time_spent}")
    #                                 total_duration_seconds += time_spent.total_seconds()
    #
    #             # Update previous state and timestamp
    #             previous_state = current_state
    #             previous_timestamp = current_timestamp
    #
    #         # Format total duration as HH:MM:SS
    #         total_duration = str(timedelta(seconds=total_duration_seconds))
    #
    #         # Build a formatted string representation of state durations
    #         state_durations_str = "\n".join(f"{key}: {str(value)}" for key, value in state_durations.items())
    #         print(f"Total Duration for record {record}: {total_duration}")
    #         print(f"State Durations for record {record}:\n{state_durations_str}")
    #
    #         # Set the formatted total duration and state durations to the record
    #         record.total_duration = total_duration
    #         record.state_durations = state_durations_str


    total_duration = fields.Char(string=' Duration (Hours)',compute='_compute_total_duration',store=True)
    state_durations = fields.Char(compute='_compute_state_durations', string='State Durations',  store=True)
    key_duration = fields.Char( string='key Durations',  store=True)


class StateDuration(models.Model):
    _name = 'state.duration'

    your_model_id = fields.Many2one('sla.monitor', string='Your Model')
    state_transition = fields.Char(string='State Transition')
    duration = fields.Float(string='Duration (seconds)')

