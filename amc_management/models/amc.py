from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import base64
from odoo.exceptions import UserError
from odoo.http import request
from io import BytesIO
import csv
import io
import base64
import odoo

from odoo.tools import config
import os

from odoo import models, http


class customers(models.Model):
    _name = "amc.customers"
    _inherit = 'mail.thread'
    _description = "amc"
    _rec_name = "name"
    _order = 'name_seq DESC'

    name = fields.Char(string="SO No")
    age = fields.Integer(string="Age")
    partner_id = fields.Many2one('res.partner', string="Company Name", required=True, tracking=True)
    order_id = fields.Many2one('sale.order', string="Service", tracking=True)
    description = fields.Char(string="Description", tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_Date = fields.Date(string="End Date", tracking=True)
    con_type = fields.Selection([('amc', 'Amc'), ('warranty', 'Warranty')], string="Contract Type", tracking=True,
                                default='amc')
    con_name = fields.Char(string="Contract Name", tracking=True)
    service = fields.Selection([('standard', 'Standard'), ('24x7', '24/7')], string="Service Level Agreement",
                               tracking=True)

    con_cost = fields.Integer(string="cost", tracking=True, widget="monetary")
    status = fields.Selection([('live', 'Live'), ('expired', 'Expired'), ('draft', 'Draft')], compute='_compute_status',
                              string="Status", tracking=True)
    contract_test = fields.Char(string="Contract Name")
    # duration_years = fields.Integer(string="Duration Years", compute="_compute_duration", store=True)
    duration = fields.Char(string="Duration", compute="_compute_duration", store=True)
    # assign_amc_ids = fields.One2many('confirm.amc', 'assign_amc_id', string='Assign Ticket')
    # ref = fields.Char(string="Contract ID", default=lambda self: _('New'))
    product_ids = fields.One2many('asset.lines', 'asset_id', string='Selected Products',
                                  help="Select one or more products")
    asset_upload_ids = fields.One2many('upload.asset', 'asset_upload_id', string='Uploaded Assets',
                                       domain="[('asset_upload_id', '=', id)]")
    name_seq = fields.Char(string="Contract ID", default=lambda self: _('New'))
    active = fields.Boolean(default=True)
    confirm_amc = fields.Integer(string="Confirm_amc")
    po_date = fields.Date(string="PO Contract Date", tracking=True)
    area_of_support = fields.Char(string="Area Of Support", tracking=True)
    monthly_visit = fields.Integer(string="Monthly Scoped Visits", tracking=True)
    yearly_visit = fields.Integer(string="Yearly Preventive Maintenance Visits", tracking=True)
    location = fields.Char(string="Location", tracking=True)
    vendor = fields.Char(string="Vendor", tracking=True)
    penalty_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Penalty Applicable",
        default='no',
        widget='radio', options={'horizontal': True}
    )
    state = fields.Selection([
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='open')
    asset_name = fields.Char(string="ASSET")
    asset_tag = fields.Char(string="ASSET TAG")
    serial_no = fields.Integer(string="SERIAL NO")
    contract_name = fields.Char(string="Contract Name")
    file_data_ids = fields.One2many('cancel.ticket.wizard', 'amc_customer_id', string="File Data")
    amc_report_pdf = fields.Binary(string="AMC Report PDF", readonly=True)
    commentbox = fields.Text(string="Add Comments")
    duration_months = fields.Integer(string="Duration (months)", default=0)
    end_amc_date = fields.Date(string="End Date", compute="_compute_end_date", store=True)
    status_amc = fields.Selection([('live','Live'),('expired','Expired'),('draft','Draft')] ,string = "Status" ,default = 'draft',tracking=True, store=True)
    amc_amount = fields.Integer(string="AMC Fee")
    amc_fee = fields.Float(string="AMC Amount")
    total_asset_count = fields.Integer(string="Total Asset Count", compute='_compute_total_asset_count', store=True)
    total_ticket_count = fields.Integer(string="Total Ticket Count", compute='_compute_total_ticket_count', store=True)
    maintenance_customer_id = fields.Many2one(
        'maintenance.customers',
        string="Maintenance Customer",
        tracking=True)

    @api.depends('order_id.ticket_ids')
    def _compute_ticket_count(self):
        for customer in self:
            customer.ticket_count = len(customer.order_id.ticket_ids)

    @api.depends('start_date', 'duration_months')
    def _compute_end_date(self):
        for record in self:
            if record.start_date and record.duration_months:
                start_date = fields.Date.from_string(record.start_date)
                end_amc_date = start_date + relativedelta(months=record.duration_months)
                record.end_amc_date = end_amc_date

    @api.depends('asset_upload_ids')
    def _compute_total_asset_count(self):
        for customer in self:
            customer.total_asset_count = len(customer.asset_upload_ids)


    # @api.depends('name')
    # def _compute_asset_count(self):
    #     for customer in self:
    #         if customer.name:
    #             customer.asset_count = self.env['upload.asset'].search_count([('asset_upload_id', '=', customer.name)])
    #         else:
    #             customer.asset_count = 0


    # def print_uploaded_assets(self):
    #     for customer in self:
    #         print(f"Customer: {customer.name}")
    #         for upload_asset in customer.asset_upload_ids:
    #             print(f"Asset Name: {upload_asset.asset_name}")
    #             print(f"Asset Tag: {upload_asset.asset_tag}")
    #             print(f"Serial No: {upload_asset.serial_no}")
    #             print(f"Warranty Start Date: {upload_asset.wty_start}")
    #             print(f"Vendor: {upload_asset.vendor}")
    #             print("\n")

    # def action_cancel(self):
    #     action = self.env.ref('amc_management.action_cancel_ticket').read()[0]
    #     return action
    def is_expired(self):
        return self.end_Date < datetime.today().date()

    # def action_renew_amc(self):
    #     # Logic to renew the AMC record
    #     self.write({
    #         'start_date': fields.Date.today(),  # Set start date to current date
    #         'end_Date': self.end_Date + timedelta(days=365),  # Extend expiration by 1 year
    #         # Other fields you want to update during renewal
    #     })

    def action_send_mail(self):
        template = self.env.ref("amc_management.amc_contract_template")
        for rec in self:
            if rec.partner_id.email:
                template.send_mail(rec.id, force_send=False)
            else:
                raise UserError("Customer Email Address Not Valid")

    def action_cancel(self):
        return {
            'name': 'Import Products',
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.ticket.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    previous_so_no = fields.Char(string='Previous SO No')

    @api.onchange('previous_so_no')
    def onchange_previous_so_no(self):
        if self.previous_so_no:
            previous_amc_record = self.env['amc.customers'].search([('name', '=', self.previous_so_no)], limit=1)
            if previous_amc_record:
                self.asset_upload_ids = [(6, 0, previous_amc_record.asset_upload_ids.ids)]
        else:
            self.asset_upload_ids = False

    # def action_cancel(self):
    #     return {
    #         'name': 'Upload CSV',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'res_model': 'cancel.ticket.wizard',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'context': {
    #             'default_amc_customer_id': self.id,
    #             # Assuming you have an amc_customer_id field in cancel.ticket.wizard
    #         }
    #     }

    # @api.onchange('order_id')
    # def onchange_order_id(self):
    #     if self.order_id:
    #         amc_customer = self.env['amc.customers'].browse(self.order_id.id)
    #         product_ids = amc_customer.product_ids.ids
    #         return {'domain': {'product_id': [('id', 'in', product_ids)]}}
    #     else:
    #         return {'domain': {'product_id': []}}

    # @api.depends('product_ids')
    # def _compute_selected_products(self):
    #     for record in self:
    #         record.selected_products = ', '.join(record.product_ids.mapped('name'))
    #
    # selected_products = fields.Char(string="Selected Products", compute="_compute_selected_products", store=True)

    # @api.onchange('order_id')
    # def onchange_order_id(self):
    #    self.name_seq=self.order_id.id

    # @api.onchange('name')
    # def onchange_name(self):
    #    self.ref=self.name
    # @api.model
    # def create_maintenance_customer(self, amc_customer_id):
    #     # Retrieve the AMC customer record
    #     amc_customer = self.browse(amc_customer_id)
    #
    #     # Create a record in the maintenance.customers model
    #     maintenance_customers = self.env['maintenance.customers']
    #     maintenance_customer_id = maintenance_customers.create({
    #         'status': amc_customer.status,
    #         # Add other fields as needed
    #     })
    #
    #     return maintenance_customer_id
    # @api.depends('start_date', 'end_amc_date', 'status')
    @api.depends('start_date', 'end_amc_date', 'status')
    def _compute_duration(self):
        for record in self:
            if record.status != 'expired' and record.start_date and record.end_amc_date:
                today = fields.Date.context_today(self)
                start_date = record.start_date  # No need to call date() on start_date
                end_date = record.end_amc_date  # No need to call date() on end_amc_date

                if start_date <= today <= end_date:
                    delta = relativedelta(end_date, today)
                    record.duration = f"{delta.years} year{'' if delta.years == 1 else 's'} {delta.months} month{'' if delta.months == 1 else 's'} {delta.days} day{'' if delta.days == 1 else 's'}"

                elif today < start_date:
                    delta = relativedelta(end_date, start_date)
                    record.duration = f"{delta.years} year{'' if delta.years == 1 else 's'} {delta.months} month{'' if delta.months == 1 else 's'} {delta.days} day{'' if delta.days == 1 else 's'}"


                else:
                    record.duration = "Expired"
            else:
                record.duration = ""

    def _update_duration(self):
        records = self.env['amc.customers'].search([])
        for record in records:
            # Calculate duration logic here, similar to _compute_duration
            if record.status != 'expired' and record.start_date and record.end_amc_date:
                today = fields.Date.context_today(self)
                start_date = record.start_date
                end_date = record.end_amc_date

                if start_date <= today <= end_date:
                    delta = relativedelta(end_date, today)
                    record.duration = f"{delta.years} year{'' if delta.years == 1 else 's'} {delta.months} month{'' if delta.months == 1 else 's'} {delta.days} day{'' if delta.days == 1 else 's'}"

                elif today < start_date:
                    delta = relativedelta(end_date, start_date)
                    record.duration = f"{delta.years} year{'' if delta.years == 1 else 's'} {delta.months} month{'' if delta.months == 1 else 's'} {delta.days} day{'' if delta.days == 1 else 's'}"

                else:
                    record.duration = "Expired"
            else:
                record.duration = ""





    def action_preview_contract(self, ids=None):
        # Add your report generation logic here
        # You can use the Odoo report mechanism or any other method to generate the report
        return self.env.ref('amc_management.report_template_id').report_action(self)

    # def get_active_contracts_count(self):
    #     # Calculate the count of active contracts
    #     active_contracts = self.search_count([('status', '=', 'live')])
    #     return active_contracts


    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     for rec in self:
    #         return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         order_id = f' {rec.name_seq} - {rec.order_id}'
    #         res.append((rec.name,order_id))
    #     return res

    # @api.depends('start_date', 'end_date')
    # def _compute_is_contract_valid(self):
    #     for record in self:
    #         today = fields.Date.today()
    #         if record.start_date and record.end_date:
    #             if record.start_date <= today <= record.end_date:
    #                 record.is_contract_valid = 'active'
    #             else:
    #                 record.is_contract_valid = 'expired'
    #         else:
    #             record.is_contract_valid = 'expired'

    # @api.depends('age')
    # def _onchange_age(self):
    #       for rec in self:
    #           if rec.age >0:
    #               rec.status = "live"
    #           elif rec.start_date or rec.end_Date:
    #               rec.status = "expired"
    #           else:
    #               rec.status = "draft"
    # @api.onchange('start_date','end_Date')
    # def calculate_date(self):
    #     for rec in self:
    #         if rec.start_date and rec.end_Date:
    #             d1 = datetime.strptime(str(rec.start_date), '%Y-%m-%d')
    #             d2 = datetime.strptime(str(rec.end_Date), '%Y-%m-%d')
    #             d3 = d2 - d1
    #             rec.age = str(d3.days)
    #
    #         else:
    #             rec.age = 0

    @api.depends('start_date', 'end_amc_date')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if record.start_date and record.end_amc_date:
                if record.start_date <= today <= record.end_amc_date:
                    record.status = 'live'
                elif today > record.end_amc_date:
                    record.status = 'expired'
                else:
                    record.status = 'draft'
            else:
                record.status = 'draft'

    def export_related_assets(self):
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Write CSV headers
        csv_writer.writerow(['ASSET', 'ASSET TAG', 'SERIAL NO', 'WTY Start DATE', 'VENDOR', 'asset_upload_id'])

        # Write asset data to CSV
        for asset in self.asset_upload_ids:
            csv_writer.writerow([asset.asset_name,asset.asset_tag,asset.serial_no, asset.wty_start, asset.vendor, asset.name])

        # Get file content as a bytes string
        csv_data = csv_buffer.getvalue().encode()

        # Encode the CSV data to base64
        csv_data_base64 = base64.b64encode(csv_data)

        # Create a new attachment record to store the CSV file
        attachment = self.env['ir.attachment'].create({
            'name': 'asset_records.csv',
            'datas': csv_data_base64,
            'res_model': 'maintenance.customers',
            'res_id': self.id,
            'type': 'binary'
        })

        # Provide a download link for the user
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s' % (attachment.id),
            'target': 'self',
        }
        # related_assets = self.env['upload.asset'].search([('asset_upload_id', '=', self.id)])
        # asset_records = self.asset_upload_ids
        # output = io.StringIO()
        # csv_writer = csv.writer(output)
        # header = ['Asset Name', 'Asset Tag', 'Serial No', 'Warranty Start', 'Vendor']  # Update with actual field names
        # csv_writer.writerow(header)
        # for asset in asset_records:
        #     csv_writer.writerow([
        #         asset.asset_name,
        #         asset.asset_tag,
        #         asset.serial_no,
        #         asset.wty_start,
        #         asset.vendor
        #
        #         # Add other fields as needed
        #     ])
        #     csv_data = output.getvalue()
        #     output.close()
        #     current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #     file_name = f"asset_records_{current_datetime}.csv"
        #
        #     # Specify the file path where the CSV file will be created
        #     export_dir = '/home/hadi/Downloads'  # Update with your export directory
        #     file_path = os.path.join(export_dir, file_name)


            # Create the directory if it doesn't exist
            # os.makedirs(os.path.dirname(file_path), exist_ok=True)
            #
            # # Write CSV data to the file
            # with open(file_path, 'w', newline='') as csv_file:
            #     csv_file.write(csv_data)
            #
            # # Return the file path
            # return file_path
            # csv_data = output.getvalue()
        # output.close()
        # file_name = 'asset_records.csv'
        # file_path = os.path.join(config.get('data_dir', ''), 'exports', file_name)
        # # file_path = '/home/hadi/Downloads/asset_records.csv'  # Update with the desired file path
        # os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # with open(file_path, 'w', newline='') as csv_file:
        #     csv_file.write(csv_data)
        # return file_path

    # class MaintenanceCustomersController(http.Controller):
    #
    #     @http.route('/web/binary/download_asset_records', type='http', auth='user')
    #     def action_export_asset_records(self, **kwargs):
    #         maintenance_customer_id = kwargs.get('amc_customers_id')
    #         if maintenance_customer_id:
    #             maintenance_customer = request.env['amc.customers'].browse(int(maintenance_customer_id))
    #             if maintenance_customer:
    #                 # Create a CSV writer object
    #                 output = io.StringIO()
    #                 csv_writer = csv.writer(output)
    #
    #                 # Write header row
    #                 header = ['asset_name','serial_no']
    #                 csv_writer.writerow(header)
    #
    #                 # Write asset records
    #                 asset_records = maintenance_customer.asset_upload_ids
    #                 for asset in asset_records:
    #                     csv_writer.writerow([
    #                         asset.asset_name,
    #                         asset.serial_no,
    #                     ])
    #
    #                 # Return CSV data
    #                 csv_data = output.getvalue().encode('utf-8')
    #                 return request.make_response(csv_data,
    #                                              headers=[('Content-Type', 'text/csv'),
    #                                                       ('Content-Disposition',
    #                                                        'attachment; filename=asset_records.csv')])
    #
    #         return request.not_found()

    class ConfirmAmc(models.Model):
        _name = "confirm.amc"
        _description = "confirm amc"

        partner_id = fields.Many2one('sale.order', string="Technician/Engineer")
        emp_id = fields.Many2one('hr.employee', string="Technician/Engineer")
        status = fields.Selection([('open', 'Open'), ('assigned', 'Assigned')])
        rem = fields.Text(string="Remarks")
        assign_amc_id = fields.Many2one('amc.customers', string="Assign To")

    #
    # def create_amc(self,vals_list):
    #     for vals in vals_list
    #         vals
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('amc.customers')
        return super(customers, self).create(vals_list)


class AssetLines(models.Model):
    _name = "asset.lines"
    _description = "Asset Lines"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product')
    internal_reference = fields.Char(related='product_id.default_code')
    sale_price = fields.Float(related='product_id.list_price')
    cost = fields.Float(related='product_id.standard_price')
    asset_id = fields.Many2one('amc.customers', string='assets')
    asset_customer_id = fields.Many2one('maintenance.customers', string="amc_management")


class UploadAssets(models.Model):
    _name = "upload.asset"
    _description = "upload asset"
    _rec_name = "asset_name"

    asset_name = fields.Char(string="ASSET")
    asset_tag = fields.Char(string="ASSET TAG")
    serial_no = fields.Integer(string="SERIAL NO")
    wty_start = fields.Date(string="WTY START_DATE")
    vendor = fields.Char(string="VENDOR")
    asset_upload_id = fields.Many2one('amc.customers', string="SO NO")
    asset_service_id = fields.Many2one('maintenance.customers', string="tes")
    name = fields.Char(string="ids", related='asset_upload_id.name')
    asset_number = fields.Char(string="id")
    ref = fields.Char(string="reference", default=lambda self: _('New'))

    total_asset_count = fields.Integer(string="Total Asset Count", compute='_compute_total_asset_count', store=True)

    @api.depends('asset_upload_id.asset_upload_ids')
    def _compute_total_asset_count(self):
        for record in self:
            if record.asset_upload_id:
                record.total_asset_count = len(record.asset_upload_id.asset_upload_ids)
            else:
                record.total_asset_count = 0


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('upload.asset')
        return super(UploadAssets, self).create(vals_list)



class Framework(models.Model):
    _name = "frame.work"
    _inherit = "amc.customers"

class BoardBoard(models.Model):
    _name = 'board.frame'
    _inherit = 'board.board'

    active_contracts_count = fields.Integer(string='Active Contracts Count', compute='_compute_active_contracts_count')

    def _compute_active_contracts_count(self):
        # Your computation logic to count active contracts
        # Example:
        active_contracts = self.env['amc.customers'].search_count([('status', '=', 'live')])
        for record in self:
            record.active_contracts_count = active_contracts

