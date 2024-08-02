import json
from datetime import date, datetime,timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class customers(models.Model):
    _name = "maintenance.customers"
    _inherit = 'mail.thread'
    _description = "maintenance"
    _rec_name = "order_id"




    partner_id = fields.Many2one('res.partner', string="Customer", required=True, tracking=True,ondelete='restrict',options={'no_create': True})
    # amc_customer_id = fields.Many2one('product.template', string="AMC Customer", domain="[('partner_id', '=', partner_id)]")
    service_type = fields.Selection([('amc', 'AMC'), ('warranty', 'Warranty'),('internal','Internal'),('ksa','KSA'),('qatar','Qatar'),('oman','Oman')], string="Service Type", tracking=True,required=True)
    cont_type = fields.Selection([('AMC RENEWAL', 'amc renewal')], string="Contract", tracking=True)
    ticket_type = fields.Selection([('incident request', 'Incident Request'), ('service request', 'Service Request')],
                                   string="Ticket Type", tracking=True)
    mode_ticket = fields.Selection([('email', 'Email'), ('phone call', 'Phone Call')], string="Ticket Mode", tracking=True)

    category_type = fields.Selection([('network', 'Network'), ('wireless', 'Wireless')], string="Category")
    description = fields.Text(string="Description",tracking=True)
    Assignedto = fields.Char(string="Assigned_To", tracking=True)
    priority = fields.Selection([('critical', 'Critical'), ('moderate', 'Moderate'),('minimal', 'Minimal')], string="priority")
    impact_type = fields.Selection([
        ('affects_department', 'Affects Department/Whole Office'),
        ('affects_single_site', 'Affects Single Site/Department'),
        ('executive_user', 'Executive User'),
        ('affects_user', 'Affects User')],
        string="Impact", tracking=True)

    urgency = fields.Selection([
        ('high', 'High'),
        ('low', 'Low'),
        ('system down', 'System Down'),
        ('urgent', 'Urgent')],
        string="Urgency")

    sla = fields.Selection([
        ('critical', 'Critical'),
        ('moderate', 'Moderate'),
        ('minimal', 'Minimal')],
        string="SLA",compute='_compute_priority',store=True,default=False)
    assign_ticket_ids = fields.One2many('assign.ticket.line', 'assign_id', string='Assign Ticket')
    name = fields.Many2one('hr.employee', string="Employee Name" , tracking=True)
    order_id = fields.Many2one('amc.customers', string="AMC's", tracking=True)
    rem = fields.Text(string="Remarks")
    contract_id = fields.Many2one('')
    conid = fields.Integer('')
    name_seq = fields.Char(string = "ContractId", related = 'order_id.name_seq')
    ref = fields.Char(string="Reference", default=lambda self: _('New'))
    # order_id_domain = fields.Char(compute="_compute_order_id_domain",readonly="True" , store=True)
    active = fields.Boolean(default=True)
    start_date = fields.Datetime(string="Date", tracking=True, default = datetime.today())
    end_Date = fields.Date(string="End Date", tracking=True)
    # amc_customer_id = fields.Many2one('amc.customers', string='AMC Customer')
    amc_age = fields.Integer(string='AMC Age', store=True)
    status = fields.Selection([('live','Live'),('expired','Expired')],string = "Status",related = 'order_id.status' ,tracking=True)
    product_ids = fields.One2many('asset.lines','asset_customer_id', string="",related='order_id.product_ids')
    pro_id = fields.Many2one('asset.lines',string="Asset")
    asset_service_ids = fields.One2many('upload.asset','asset_service_id',string="")
    ass_id = fields.Many2one('upload.asset',string="Asset", tracking=True)
    site_location = fields.Boolean("Is Site location Different From Customer Address?", default=False, tracking=True)
    Site_name = fields.Char(string= "Site Address",tracking=True)
    Site_number = fields.Integer(string="Site Contact Number",tracking=True)
    cancellation_source = fields.Selection([
        ('manual', 'Manually Cancelled'),
        ('auto', 'Automatically Cancelled')
    ], string='Cancellation Source', default=False)
    escalation_email_sent = fields.Boolean('escalation_email_sent',default=False)
    second_escalation_email_sent = fields.Boolean('second_escalation_email_sent',default=False)


    sla_monitor_ids = fields.One2many('sla.monitor', 'ticket_id', string='sla monitor',
                                  help="Select one or more products",)
    monitor_sla_id = fields.Many2one('sla.monitor',string='sla')
    comments = fields.Text(string="Comments")
    state = fields.Selection([
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('work in progress', 'Work In Progress'),
        ('waiting for customer', 'Waiting For Customer'),
        ('waiting for vendor', 'Waiting For Vendor'),
        ('resolved', 'Resolved'),
        ('done', 'Done'),
        ('cancel', 'Closed'),
        ('not live', 'Not Live'),
        ('test', 'Test'),
        ('reopen','Reopen')
    ], default = 'not live')
    emp_ids = fields.Many2many('hr.employee', string="Assigned To")
    progress = fields.Integer(string="progress",compute='_compute_progress')
    contract_name = fields.Char(string="Contract Name", related='order_id.contract_test')
    # contract_name = fields.Many2one(
    #     'amc.customers',
    #     string='Contract Name',
    #     domain="[('partner_id', '=', partner_id)]",
    #     display_name='contract_test'  # Specify the field to use for display
    # )
    sla_days = fields.Selection([
        ('same business day', 'Same Business Day'),
        ('next business day(1-2 days)', 'Next Business Day(1-2 Days)'),
        ('2-3 days', '2-3 Days')
    ], string='SLA Days',compute='_compute_sla_days',default=False)

    domain_id = fields.Many2one('amc.domain', string="Sub Category", )
    cat_test = fields.Selection([('network', 'NETWORK'), ('wireless', 'WIRELESS')])
    category_id = fields.Many2one('amc.domain', string='Category')
    # sub_cat = fields.Selection([('router', 'ROUTER'), ('switch', 'SWITCH')])
    device_type = fields.Selection([('Cisco','CISCO'),('hp','HP'),('fortinet', 'FORTINET'),('advantech','ADVANTECH'),('huawei','HUAWEI')])
    device_type_id = fields.Many2one('amc.brand', string='Device Type')
    amc_category_id = fields.Many2one('amc.category', string='test')
    subject_des = fields.Char(string='Subject',tracking=True)

    sla_broken = fields.Boolean(compute='_compute_sla_broken', store=True)
    assigned_remarks = fields.Text(string="Assigned Remarks")
    open_remarks = fields.Text(string="Open Remarks")
    # not_live_remarks = fields.Text(string="Not Live Remarks")
    resolved_remarks = fields.Text(string="Resolved Remarks")
    waiting_for_customer_remarks = fields.Text(string="Waiting For Customer Remarks")
    waiting_for_vendor_remarks = fields.Text(string="Waiting For Vendor Remarks")
    work_in_progress_remarks = fields.Text(string="Work In Progress Remarks")
    selected_state = fields.Selection([
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('work in progress', 'Work In Progress'),
        ('waiting for customer', 'Waiting For Customer'),
        ('waiting for vendor', 'Waiting For Vendor'),
        ('resolved', 'Resolved'),
    ], string="Select State")
    selected_remarks = fields.Text(string="Selected State Remarks", compute='_compute_selected_remarks')

    total_ticket_count = fields.Integer(string="Total Ticket Count", compute='_compute_total_ticket_count', store=True)
    resolution = fields.Text(string="Resolution" )
    eng_name_id = fields.Many2many('eng.domain', string='Engineer')

    @api.depends('order_id.maintenance_customer_id')
    def _compute_total_ticket_count(self):
        for record in self:
            if record.order_id:
                record.total_ticket_count = len(record.order_id.maintenance_customer_id)
            else:
                record.total_ticket_count = 0


    @api.depends('selected_state')
    def _compute_selected_remarks(self):
        for record in self:
            if record.selected_state:
                field_name = record.selected_state.replace(' ', '_') + '_remarks'
                record.selected_remarks = getattr(record, field_name, '')
            else:
                record.selected_remarks = False

    @api.depends('escalation_email_sent')
    def _compute_sla_broken(self):
        for record in self:
            record.sla_broken = record.escalation_email_sent

    # @api.onchange('cat_test')
    # def onchange_service_type(self):
    #     if self.service_type:
    #         amc_domain = self.env['amc.domain'].search([('category_test', '=', self.cat_test)])
    #         print(self.cat_test)
    #         category_ids = amc_domain.mapped('category_id')
    #         return {'domain': {'category_id': [('id', 'in', category_ids.ids)]}}
    #     else:
    #         return {'domain': {'category_id': []}}

    @api.onchange('amc_category_id')
    def onchange_amc_category_id(self):
        domain = []

        if self.amc_category_id:
            amc_domains = self.env['amc.domain'].search([('domain', '=', self.amc_category_id.id)])
            domain_ids = amc_domains.ids  # Get the list of IDs directly
            domain = [('id', 'in', domain_ids)]
        else:
            # If category_type is empty, domain should be set to show no records
            domain = [('id', '=', False)]
        return {'domain': {'domain_id': domain}}

    @api.onchange('domain_id')
    def onchange_domain_id(self):
        domain = []

        if self.domain_id:
            amc_brands = self.env['amc.brand'].search([('domain_id', '=', self.domain_id.id)])
            brand_ids = amc_brands.ids  # Get the list of IDs directly
            domain = [('id', 'in', brand_ids)]
        else:
            # If category_type is empty, domain should be set to show no records
            domain = [('id', '=', False)]
        return {'domain': {'device_type_id': domain}}




    @api.onchange('order_id')
    def onchange_order_id(self):
        if self.order_id:
            # Get all products linked to the selected order_id
            products = self.order_id.product_ids
            # Construct a domain to filter the available products
            domain = [('id', 'in', products.ids)]
            # Update the domain for the pro_id field
            return {'domain': {'pro_id': domain}, 'value': {'pro_id': False}}
        else:
            # If no order_id is selected, reset the domain and pro_id
            return {'domain': {'pro_id': []}, 'value': {'pro_id': False}}

    @api.depends('sla')
    def _compute_sla_days(self):
        for ticket in self:
            if ticket.sla == 'critical':
                ticket.sla_days = 'same business day'
            elif ticket.sla == 'moderate':
                ticket.sla_days = 'next business day(1-2 days)'
            elif ticket.sla == 'minimal':
                ticket.sla_days = '2-3 days'

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     """ Update domain for contract_name based on selected partner_id """
    #     if self.partner_id:
    #         return {'domain': {'contract_name': [('partner_id', '=', self.partner_id.id)]}}
    #     else:
    #         return {'domain': {'contract_name': []}}



                # @api.onchange('order_id')
    # def onchange_order_id(self):
    #     if self.order_id:
    #         # Get all products linked to the selected order_id
    #         products = self.order_id.product_ids
    #         # Construct a domain to filter the available products
    #         domain = [('id', 'in', products.ids)]
    #         # Update the domain for the pro_id field
    #         return {'domain': {'pro_id': domain}, 'value': {'pro_id': False}}
    #     else:
    #         # If no order_id is selected, reset the domain and pro_id
    #         return {'domain': {'pro_id': []}, 'value': {'pro_id': False}}
    # @api.onchange('order_id')
    # def onchange_order_id(self):
    #     if self.order_id:
    #         print(f"Selected order_id: {self.order_id.id}")
    #         amc_products = self.env['amc.customers'].search([('order_id', '=', self.order_id.id)])
    #         print(f"Matching amc_products: {amc_products.ids}")
    #         product_ids = amc_products.mapped('product_ids.id')
    #         print(f"Filtered product_ids: {product_ids}")
    #         return {'domain': {'product_ids': [('id', 'in', product_ids)]}}
    #     else:
    #         return {'domain': {'product_ids': []}}
    # @api.onchange('order_id')
    # def onchange_order_id(self):
    #     if self.order_id:
    #         amc_products = self.env['amc.customers'].search([('order_id', '=', self.order_id.id)])
    #         product_ids = amc_products.mapped('product_ids.id')
    #         return {'domain': {'product_id': [('id', 'in', product_ids)]}}
    #     else:
    #         return {'domain': {'product_id': []}}
    # @api.onchange('order_id')
    # def onchange_order_id(self):
    #     if self.order_id:
    #         return {'domain': {'product_id': [('name', '=', self.order_id.id)]}}
    # @api.depends('amc_customer_ids.product_ids')
    #     def _compute_selected_products(self):
    #         for record in self:
    #             products = record.amc_customer_ids.mapped('product_ids')
    #               record.selected_products = [(6, 0, products.ids)]

    # @api.onchange('order_id')
    # def onchange_name(self):
    #         for rec in self:
    #             return {'domain': {'product_id': [('name_seq', '=', rec.order_id.id)]}}

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         partner_id = f' {rec.ref} - {rec.partner_id}'
    #         res.append((rec.id, partner_id))
    #     return res

    # @api.depends('partner_id')
    # def _compute_order_id_domain(self):
    #    for rec in self:
    #        rec.order_id_domain = json.dumps([('partner_id', '=', rec.name_id.id)])

           # < xpath attribute
           # name = "domain" > ('id', 'in', _compute_order_id_domain)] < /xpath attribute >
    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #    self.ref=self.partner_id.id
    #
    # @api.onchange('partner_id')
    # def onchange_partners_id(self):
    #     for rec in self:
    #         domain = [('partner_id', '=', rec.partner_id.id)]
    #         sale_order = self.env['sale.order'].search(domain, limit=1)
    #
    #         if sale_order:
    #             # Get the product_ids from amc.customers
    #             product_ids = sale_order.product_ids.ids
    #
    #             # Find related amc.customers records
    #             amc_records = self.env['amc.customers'].search([('order_id', '=', sale_order.id)])
    #
    #             # Collect product_ids from related amc.customers
    #             for amc_record in amc_records:
    #                 product_ids.extend(amc_record.product_ids.ids)
    #
    #             # Update the domain dynamically for product_id
    #             product_id_domain = [('id', 'in', product_ids)]
    #
    #             return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)],
    #                                'product_id': product_id_domain}}
    #         else:
    #             return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    @api.depends('impact_type', 'urgency')
    def _compute_priority(self):
        for record in self:
            if record.impact_type and record.urgency:
                sla_matrix = {
                    'affects_department': {
                        'high': 'critical',
                        'low': 'moderate',
                        'system_down': 'critical',
                        'urgent': 'critical'
                    },
                    'affects_single_site': {
                        'high': 'moderate',
                        'low': 'minimal',
                        'system_down': 'critical',
                        'urgent': 'critical'
                    },
                    'executive_user': {
                        'high': 'critical',
                        'low': 'moderate',
                        'system_down': 'critical',
                        'urgent': 'critical'
                    },
                    'affects_user': {
                        'high': 'critical',
                        'low': 'moderate',
                        'system_down': 'critical',
                        'urgent': 'critical'
                    }
                }
                record.sla = sla_matrix.get(record.impact_type, {}).get(record.urgency, 'minimal')
            else:
                record.sla = 'minimal'
    # @api.model
    # def create(self, values):
    #     if 'status' in values and values['status'] != 'live':
    #         raise UserError("Cannot create a record with status other than 'live'")
    #
    #     return super(maintenance.customers, self).create(values)
    #
    # def write(self, values):
    #     if 'state' in values and values['state'] != 'open' and self.status != 'live':
    #         raise UserError("Cannot change state to '{}' when status is not 'live'".format(values['state']))
    #
    #     return super(maintenance.customers, self).write(values)

    # @api.onchange('partner_id')
    # def onchange_partners_id(self):
    #     for rec in self:
    #         return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    # @api.onchange('partner_id')
    # def onchange_partners_id(self):
    #     domain = [('partner_id', '=', self.partner_id.id), ('status_amc', '=', 'live')]
    #     return {'domain': {'order_id': domain}}
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        domain = [('partner_id', '=', self.partner_id.id)]
        order_ids = self.env['amc.customers'].search(domain).filtered(lambda r: r.status == 'live').ids
        return {'domain': {'order_id': [('id', 'in', order_ids)]}}

    @api.onchange('service_type')
    def onchange_service_type(self):
        if self.service_type:
            amc_customers = self.env['amc.customers'].search([('con_type', '=', self.service_type)])
            partner_ids = amc_customers.mapped('partner_id')
            return {'domain': {'partner_id': [('id', 'in', partner_ids.ids)]}}
        else:
            return {'domain': {'partner_id': []}}

    # @api.onchange('service_type')
    # def onchange_service_id(self):
    #     for rec in self:
    #
    #         return {'domain': {'partner_id': [('order_id.con_tye', '=', rec.service_type)]}}

    # @api.onchange('status')
    # def onchange_status_id(self):
    #     for rec in self:
    #         return {'domain':{'order_id':[('status','=','live')]}}

    @api.model
    def create(self, vals):
        ticket = super(customers, self).create(vals)
        print("Create - Old State:", ticket.state)
        print("Create - New State:", vals.get('state'))
        ticket.sla_state_change(vals.get('state'))  # Pass new state through vals
        return ticket

    def write(self, vals):
        res = super(customers, self).write(vals)
        if 'state' in vals:
            for ticket in self:
                print("Write - Old State:", ticket.state)
                print("Write - New State:", vals['state'])
                ticket.sla_state_change(vals['state'])  # Pass new state through vals
        return res

    def sla_state_change(self, new_state):
        sla_monitor_vals = []
        for ticket in self:
            sla_monitor_vals.append({
                'ticket_id': ticket.id,
                'old_state': ticket.state,
                'new_state': new_state,  # Use new_state passed as an argument
                'timestamp': fields.Datetime.now()
            })
            print(ticket.state, new_state)
        self.env['sla.monitor'].create(sla_monitor_vals)


    def action_open(self):
        for rec in self:
            if rec.status =='live':
                rec.state = 'open'
                template = self.env.ref("amc_management.amc_helpdesk_template")
                for rec in self:
                    if rec.partner_id.email:
                        template.send_mail(rec.id, force_send=False)
                    else:
                        raise UserError("Customer Email Address Not Valid")
            else:
                raise UserError("AMC NOT LIVE! Please Contact Help Desk.")

    def action_assigned(self):
        for rec in self:
            if rec.status == 'live':
                rec.state = 'assigned'
                template = self.env.ref("amc_management.amc_assigned_template")
                for rec in self:
                    if rec.partner_id.email:
                        template.send_mail(rec.id, force_send=False)
                    else:
                        raise UserError("Customer Email Address Not Valid")
            elif rec.status == 'draft':
                raise UserError(_("AMC NOT LIVE!"))
            else:
                raise UserError(_("AMC Expired! You cannot assign a ticket to an expired AMC."))


    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_work_in_progress(self):
        template = self.env.ref("amc_management.amc_work_in_progress_template")
        for rec in self:
            rec.state = 'work in progress'
            if rec.partner_id.email:
                template.send_mail(rec.id, force_send=False)
            else:
                raise UserError("Customer Email Address Not Valid")

    def action_waiting_for_customer(self):
        template = self.env.ref("amc_management.amc_waiting_for_customer_template")
        for rec in self:
            if rec.status == 'live':
                rec.state = 'waiting for customer'
            if rec.partner_id.email:
                template.send_mail(rec.id, force_send=False)
            else:
                raise UserError("Customer Email Address Not Valid")

    def action_waiting_for_vendor(self):
        template = self.env.ref("amc_management.amc_waiting_for_vendor_template")
        for rec in self:
            if rec.status == 'live':
                rec.state = 'waiting for vendor'
            if rec.partner_id.email:
                template.send_mail(rec.id, force_send=False)
            else:
                raise UserError("Customer Email Address Not Valid")

    def action_resolved(self):
        template = self.env.ref("amc_management.amc_resolved_template")
        for rec in self:
            if rec.status == 'live':
                rec.state = 'resolved'
            if rec.partner_id.email:
                template.send_mail(rec.id, force_send=False)
            else:
                raise UserError("Customer Email Address Not Valid")

    def action_reopen(self):
        for rec in self:
            if rec.status =='live':
                rec.state = 'reopen'
            else:
                raise UserError("User Error")

    def action_knowledge(self):
        for record in self:
            self.env['maintenance.knowledge.base.product'].create({
                    'customer_id': record.id,
                    'amc_category_id': record.amc_category_id,
                    'domain_id': record.domain_id,
                    'device_type_id': record.device_type_id,
                    'subject_des': record.subject_des,
                    'description': record.description,
                })






    def check_open_tickets(self):
        # Define your criteria for auto-changing states (e.g., based on days)

        days_threshold_live = 2

        # # Find records that need to be moved from 'draft' to 'live'
        # records_to_live = self.search([
        #     ('state', '=', 'draft'),
        #     ('creation_date', '<=', fields.Date.today() - days_threshold_draft)
        # ])
        #
        # # Update the state to 'live' and set the cancellation source to 'auto' for each record
        # records_to_live.write({
        #     'state': 'live',
        #     'cancellation_source': 'auto'
        # })

        # Find records that need to be cancelled from 'live'
        records_to_cancel = self.search([
            ('state', '=', 'resolved'),
            ('start_date', '<=', fields.Date.today() - timedelta(days=days_threshold_live))
        ])

        # Update the state to 'cancel' and set the cancellation source to 'auto' for each record
        records_to_cancel.write({
            'state': 'done',
            'cancellation_source': 'auto'
        })
        if self.state:
            self.env.ref("amc_management.amc_done_template").send_mail(self.id, force_send=False)

        # Replace 'your_module.cancel_email_template_id' with the actual ID of your email template


    @api.model
    def cron_check_open_tickets(self):
        # This method will be called periodically using a scheduled action
        self.check_open_tickets()

    def action_cancel(self):
        # Action for manually canceling records
        self.write({
            'state': 'cancel',
            'cancellation_source': 'manual'
        })


    # def action_cancel(self):
    #     # action = self.env.ref('amc_management.action_cancel_ticket').read()[0]
    #     for rec in self:
    #         rec.state = 'cancel'
    #         rec.cancellation_source = 'manual'
            # self.update({'state': 'cancel'}) if there is  multiple records



    # @staticmethod
    # def get_public_holidays(country_code, year):
    #     return holidays.CountryHoliday(country_code, years=year).items()

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
    def send_ticket_escalation_emails(self):
        # Define SLA thresholds (in hours)
        sla_thresholds = {'critical': 1, 'moderate': 4, 'minimal': 24}
        current_year = datetime.now().year
        # Define office hours
        office_start_time = 8
        office_end_time = 18

        # Define weekend days (Friday and Saturday)
        weekend_days = [4, 5]  # Friday = 4, Saturday = 5
        public_holiday_dates = self.is_public_holiday()

        # Fetch tickets
        tickets = self.env['maintenance.customers'].search(
            [('state', '=', 'open'), ('sla', 'in', ['critical', 'moderate', 'minimal'])])

        for ticket in tickets:
            if ticket.escalation_email_sent:
                continue
            creation_time = ticket.create_date
            current_time = datetime.now()
            sla_level = ticket.sla

            # Calculate time difference in hours
            time_difference_hours = (current_time - creation_time).total_seconds() / 3600

            # Adjust escalation email sending time based on SLA and ticket creation time
            if sla_level == 'critical':
                if current_time.hour >= office_end_time:
                    next_working_day = current_time + timedelta(days=1)
                    if next_working_day.weekday() in weekend_days or next_working_day in public_holiday_dates:
                        next_working_day += timedelta(days=1)
                    next_working_day = next_working_day.replace(hour=office_start_time, minute=30, second=0,
                                                                microsecond=0)
                    send_time = next_working_day
                else:
                    send_time = current_time + timedelta(hours=1)  # Send after 1 hour
            elif sla_level == 'moderate':
                if current_time.hour >= office_end_time:
                    next_working_day = current_time + timedelta(days=1)
                    if next_working_day.weekday() in weekend_days or next_working_day in public_holiday_dates:
                        next_working_day += timedelta(days=1)
                    next_working_day = next_working_day.replace(hour=office_start_time, minute=0, second=0,
                                                                microsecond=0)
                    send_time = next_working_day
                else:
                    send_time = current_time + timedelta(hours=4)  # Send after 4 hours
            elif sla_level == 'minimal':
                if current_time.hour >= office_end_time:
                    next_working_day = current_time + timedelta(days=1)
                    if next_working_day.weekday() in weekend_days or next_working_day in public_holiday_dates:
                        next_working_day += timedelta(days=1)
                    next_working_day = next_working_day.replace(hour=office_start_time, minute=0, second=0,
                                                                microsecond=0)
                    send_time = next_working_day
                else:
                    send_time = current_time + timedelta(hours=24)  # Send after 24 hours

            # Send escalation email
                if send_time > current_time:
                    self.env.ref("amc_management.amc_first_escalation_template").send_mail(ticket.id, force_send=False)
                    ticket.write({'escalation_email_sent': True, 'sla_broken': True})

            second_escalation_time = timedelta(hours=3) if sla_level == 'critical' else \
                timedelta(hours=8) if sla_level == 'moderate' else \
                    timedelta(hours=48) if sla_level == 'minimal' else None

            if second_escalation_time:
                threshold_delta = timedelta(hours=sla_thresholds[sla_level])
                if time_difference_hours >= (threshold_delta + second_escalation_time).total_seconds() / 3600:
                    # Check if the ticket is still not assigned
                    if not ticket.emp_ids:
                        self.env.ref("amc_management.amc_second_escalation_template").send_mail(ticket.id,
                                                                                                force_send=False)
                        ticket.write({'second_escalation_email_sent': True})
    #
    # def send_ticket_escalation_emails(self):
    #     # Define SLA thresholds (in hours)
    #     sla_thresholds = {'critical': 1, 'moderate': 4, 'minimal': 24}
    #     current_time = fields.Datetime.now()
    #
    #     # Define office hours
    #     office_start_time = 8
    #     office_end_time = 18
    #
    #     # Define weekend days (Friday and Saturday)
    #     weekend_days = [4, 5]  # Friday = 4, Saturday = 5
    #     public_holiday_dates = self.is_public_holiday()
    #
    #     # Fetch open tickets with critical, moderate, or minimal SLA
    #     tickets = self.env['maintenance.customers'].search([
    #         ('state', '=', 'open'),
    #         ('sla', 'in', ['critical', 'moderate', 'minimal']),
    #         ('escalation_email_sent', '=', False)
    #     ])
    #
    #     for ticket in tickets:
    #         creation_time = fields.Datetime.from_string(ticket.create_date)
    #         sla_level = ticket.sla
    #
    #         # Calculate time difference in hours
    #         time_difference_hours = (current_time - creation_time).total_seconds() / 3600
    #
    #         # Determine when to send the escalation email based on SLA level
    #         if sla_level == 'critical':
    #             next_send_time = self._calculate_next_send_time(current_time, office_end_time, weekend_days,
    #                                                             public_holiday_dates, office_start_time, 1)
    #         elif sla_level == 'moderate':
    #             next_send_time = self._calculate_next_send_time(current_time, office_end_time, weekend_days,
    #                                                             public_holiday_dates, office_start_time, 4)
    #         elif sla_level == 'minimal':
    #             next_send_time = self._calculate_next_send_time(current_time, office_end_time, weekend_days,
    #                                                             public_holiday_dates, office_start_time, 24)
    #
    #         if next_send_time and current_time < next_send_time:
    #             # Send the escalation email
    #             template_id = self.env.ref("amc_management.amc_first_escalation_template").id
    #             template = self.env['mail.template'].browse(template_id)
    #             template.send_mail(ticket.id, force_send=False)
    #             ticket.write({'escalation_email_sent': True})
    #
    #             # Calculate second escalation time
    #             second_escalation_time = timedelta(hours=3) if sla_level == 'critical' else \
    #                 timedelta(hours=8) if sla_level == 'moderate' else \
    #                     timedelta(hours=48) if sla_level == 'minimal' else None
    #
    #             if second_escalation_time and time_difference_hours >= sla_thresholds[
    #                 sla_level] + second_escalation_time:
    #                 # Check if the ticket is still not assigned
    #                 if not ticket.emp_ids:
    #                     second_template_id = self.env.ref("amc_management.amc_second_escalation_template").id
    #                     second_template = self.env['mail.template'].browse(second_template_id)
    #                     second_template.send_mail(ticket.id, force_send=False)
    #                     ticket.write({'second_escalation_email_sent': True})
    #
    # def _calculate_next_send_time(self, current_time, office_end_time, weekend_days, public_holiday_dates,
    #                               office_start_time, delay_hours):
    #     if current_time.hour >= office_end_time:
    #         next_working_day = current_time + timedelta(days=1)
    #         while next_working_day.weekday() in weekend_days or next_working_day.date() in public_holiday_dates:
    #             next_working_day += timedelta(days=1)
    #         next_working_day = next_working_day.replace(hour=office_start_time, minute=0, second=0, microsecond=0)
    #         return next_working_day
    #     else:
    #         return current_time + timedelta(hours=delay_hours)

    from datetime import datetime, timedelta
    @api.depends('state')
    def _compute_time_to_close(self):
        for ticket in self:
            if ticket.state == 'done':
                # Find the last state transition in the sla.monitor records
                last_transition = ticket.sla_monitor_ids.filtered(lambda r: r.new_state == 'done').sorted('timestamp',
                                                                                                          reverse=True)[
                                  :1]
                print(last_transition,"last ")
                if last_transition:
                    last_timestamp = fields.Datetime.from_string(last_transition.timestamp)
                    # Calculate time difference between last transition and now
                    time_diff = datetime.now() - last_timestamp
                    print(time_diff)
                    ticket.time_to_close = time_diff.total_seconds() / (60 * 60 * 24)  # Convert to days
                else:
                    ticket.time_to_close = 0
            else:
                ticket.time_to_close = 0

    average_time_to_close = fields.Float(string='Average Time to Close (days)')

    @api.model
    def compute_average_time_to_close(self):
        result = []
        employees = self.env['hr.employee'].search([])

        for employee in employees:
            for sla in ['minimal', 'moderate', 'critical']:
                tickets = self.env['maintenance.customers'].search([
                    ('emp_ids', '=', [employee.id]  ),
                    ('sla', '=', sla),
                    ('state', '=', 'done')  # Only consider closed tickets
                ])
                total_time_to_close = sum(ticket.time_to_close for ticket in tickets)
                average_time_to_close = total_time_to_close / len(tickets) if tickets else 0
                result.append({
                    'employee_id': employee.id,
                    'sla': sla,
                    'average_time_to_close': average_time_to_close,
                })
                print(employee.id)
        return result


    time_to_close = fields.Float(compute='_compute_time_to_close', string='Time to Close (days)', store=True)





    class AssignTicketLine(models.Model):
        _name = "assign.ticket.line"
        _description = "Assign Ticket"

        users_id = fields.Many2one('hr.employee', string="Technician/Engineer")
        status = fields.Selection([('open', 'Open'), ('assigned', 'Assigned')])
        rem = fields.Text(string="Remarks")
        assign_id = fields.Many2one('maintenance.customers', string="Assign To")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('maintenance.customers')
        return super(customers, self).create(vals_list)

