from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    confirm_amc = fields.Selection([('yes','Yes'),('no','No')], string = "Is This An AMC",default='no')
    start_date = fields.Date(string="start date", tracking=True)
    end_Date = fields.Date(string="end date", tracking=True)
    # age = fields.Integer(string="age")
    contract_name = fields.Char(string="Contract",tracking=True)
    amc_included = fields.Boolean("Amc Included?", default=False)
    status = fields.Selection([('live','Live'),('expired','Expired'),('draft','Draft')] ,string = "Status" ,default = 'draft',tracking=True)
    amc_type = fields.Many2one('product.template', string= "AMC Type", domain = [('id','in',[34,33,32])])
    order_line = fields.One2many('sale.order.line', 'order_id', string="Order Lines")
    amc_fee = fields.Float(string='AMC Fee')


    # confirm_amc = fields.Boolean(string = "Is this an AMC")
    @api.onchange('amc_included')
    def _onchange_amc_included(self):
        if self.amc_included:
            amc_product = self.env['product.product'].browse(42)  # Assuming 31 is the product ID for AMC
            if amc_product:
                self.order_line = [(0, 0, {
                    'product_id': amc_product.id,
                    'product_uom_qty': 1,
                    'price_unit': amc_product.list_price,
                })]
        else:
            # If amc_included is False, you might want to clear the order lines
            self.update({'order_line': [(5, 0, 0)]})

    @api.onchange('amc_type')
    def _onchange_amc_type(self):
        for rec in self:

            rec.order_line = [(2, line.id, 0) for line in rec.order_line]


            lines = [(0, 0, {
                'product_id': variant.id,
                'name': variant.display_name,
                'product_uom_qty': 1,
                'price_unit': variant.list_price,
            }) for variant in rec.amc_type.product_variant_ids]

            rec.order_line = lines

    # @api.onchange('start_date', 'end_Date', 'age')
    # def calculate_dates(self):
    #     for rec in self:
    #         if rec.start_date and rec.end_Date:
    #             d1 = datetime.strptime(str(rec.start_date), '%Y-%m-%d')
    #             d2 = datetime.strptime(str(rec.end_Date), '%Y-%m-%d')
    #             d3 = d2 - d1
    #             rec.age = str(d3.days)
    #
    #         else:
    #             rec.age = 0
    #
    # @api.depends('age')
    # def _onchange_ages(self):
    #     for rec in self:
    #         if rec.age > 0:
    #             rec.status = "live"
    #         else:
    #             rec.status = "expired"

    def action_confirm(self):
        super(SaleOrder,self).action_confirm()
        # self.mapped('line_ids.sale_line_ids')._update_registrations(confirm=True, mark_as_paid=True)
        # return res
        if self.confirm_amc == 'yes':
            print("yay")

    @api.onchange('amc_fee')
    def onchange_custom_amount(self):
        amc_product = self.env['product.product'].search([('name', '=', 'AMC Services')], limit=1)
        if amc_product:
            for line in self.order_line:
                if line.product_id == amc_product:
                    line.price_unit = self.amc_fee

    # @api.depends('amc_fee', 'order_line.product_id')
    # def _compute_unit_price(self):
    #     for order in self:
    #         for line in order.order_line:
    #             if line.product_id:
    #                 if order.amc_fee:
    #                     line.price_unit = order.amc_fee / line.product_uom_qty
    #
    # @api.onchange('order_line')
    # def onchange_order_line(self):
    #     for line in self.order_line:
    #         if line.product_id and self.amc_fee:
    #             line.price_unit = self.amc_fee / line.product_uom_qty



