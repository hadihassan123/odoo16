from odoo import models, fields, api
from collections import Counter


class SaleOrderSummary(models.Model):
    _inherit = 'sale.order'

    # sale_summary_lines = fields.One2many('purchase.order.product.summary', 'sale_order_id', string='Product Summary')
    product_summary_lines = fields.One2many('purchase.order.product.summary', 'sales_order_id', string='Product Summary')
    purchase_order_product_summary_lines = fields.One2many('purchase.order.product.summary', 'related_sale_order_id', string='Product Summary')

    def copy_product_summary_lines(self):
        for order in self:
            continue


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_summary_lines = fields.One2many('purchase.order.product.summary', 'purchase_order_id',
                                            string='Product Summary')

    related_sale_order_id = fields.Many2one('sale.order', compute='_compute_related_sale_order')

    @api.depends('origin')
    def _compute_related_sale_order(self):
        for order in self:
            order.related_sale_order_id = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)

    # def update_sale_order_line_cost(self):
    #     for order in self:
    #         sale_order = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
    #         print('name', order.origin)
    #         if sale_order:
    #             for line in order.order_line:
    #                 sale_order_line = sale_order.order_line.filtered(lambda l: l.product_id == line.product_id)
    #                 if sale_order_line:
    #                     sale_order_line.purchase_price = line.price_unit

    def update_sale_order_line_cost(self):
        for order in self:
            sale_order = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
            if sale_order:
                for line in order.order_line:
                    sale_order_line = sale_order.order_line.filtered(lambda l: l.product_id == line.product_id)
                    if sale_order_line:
                        sale_order_line.purchase_price = line.price_unit
                        # sale_order_line.product_uom_qty = line.product_qty  # Update the new field

    def add_new_products_to_sale_order(self):
        for order in self:
            sale_order = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
            if sale_order:
                purchase_order_lines = order.order_line
                existing_products_in_sale_order = sale_order.order_line.mapped('product_id')
                product_counter = Counter(line.product_id for line in purchase_order_lines)
                for product, count in product_counter.items():
                    if count > 1:
                        # Add the product with its full count to the sale order lines
                        order_line_vals = {
                            'product_id': product.id,
                            'product_uom_qty': count,
                            'product_uom': product.uom_id.id,
                            'purchase_price': product.standard_price,
                            'price_unit': 0.0,  # Set price_unit to 0.0
                            'order_id': sale_order.id,
                        }
                        new_line = self.env['sale.order.line'].create(order_line_vals)
                    else:
                        # Subtract 1 from the count if the product exists in the sale order lines
                        if product in existing_products_in_sale_order:
                            count -= 1
                        if count <= 0:
                            continue
                        order_line_vals = {
                            'product_id': product.id,
                            'product_uom_qty': count,
                            'product_uom': product.uom_id.id,
                            'purchase_price': product.standard_price,
                            'price_unit': 0.0,  # Set price_unit to 0.0
                            'order_id': sale_order.id,
                        }
                        new_line = self.env['sale.order.line'].create(order_line_vals)

    # def add_new_products_to_sale_order(self):
    #     for order in self:
    #         sale_order = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
    #         if sale_order:
    #             purchase_order_lines = order.order_line
    #             existing_products_in_sale_order = sale_order.order_line.mapped('product_id')
    #             product_counter = Counter(line.product_id for line in purchase_order_lines)
    #             for product, count in product_counter.items():
    #                 if count > 1:
    #                     # Add the product with its full count to the sale order lines
    #                     order_line_vals = {
    #                         'product_id': product.id,
    #                         'product_uom_qty': count,
    #                         'product_uom': product.uom_id.id,
    #                         'purchase_price': product.standard_price,
    #                         'price_unit': 0.0,  # Set price_unit to 0.0
    #                         'order_id': sale_order.id,
    #                     }
    #                     new_line = self.env['sale.order.line'].create(order_line_vals)
    #                 else:
    #                     # Subtract 1 from the count if the product exists in the sale order lines
    #                     if product in existing_products_in_sale_order:
    #                         count -= 1
    #                     if count <= 0:
    #                         continue
    #                     order_line_vals = {
    #                         'product_id': product.id,
    #                         'product_uom_qty': count,
    #                         'product_uom': product.uom_id.id,
    #                         'purchase_price': product.standard_price,
    #                         'price_unit': 0.0,  # Set price_unit to 0.0
    #                         'order_id': sale_order.id,
    #                     }
    #                     new_line = self.env['sale.order.line'].create(order_line_vals)

    # Add the product to the list of existing products

    # def add_new_products_to_sale_order(self):
    #     for order in self:
    #         sale_order = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
    #         if sale_order:
    #             for line in order.order_line:
    #                 if line.product_id not in sale_order.order_line.mapped('product_id'):
    #                     order_line_vals = {
    #                         'product_id': line.product_id.id,
    #                         'product_uom_qty': line.product_qty,
    #                         'product_uom': line.product_uom.id,
    #                         'purchase_price': line.price_unit,
    #                         'price_unit': 0.0,  # Set price_unit to 0.0
    #                         'order_id': sale_order.id,
    #                     }
    #                     self.env['sale.order.line'].create(order_line_vals)



    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        print("yay")

        self.update_sale_order_line_cost()
        self.add_new_products_to_sale_order()

        revised_prices = False
        for line in self.product_summary_lines:
            if line.revised_unit_price != line.unit_price:
                revised_prices = True
                break

        if revised_prices:
            # Get the salesperson from the related sale order
            sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
            if sale_order:
                salesperson = sale_order.user_id

                # Send an email to the salesperson
                if salesperson and salesperson.email:
                    try:
                        mail_template = self.env.ref("rfq_management.email_template_revised_prices")
                        mail_template.send_mail(self.id, force_send=True, email_values={'email_to': salesperson.email})
                    except ValueError:
                        # Handle the case where the email template is not found
                        print("Error: Email template 'purchase.email_template_revised_prices' not found")

        return res

    # def button_confirm(self):
    #     res = super(PurchaseOrder, self).button_confirm()
    #     print("yay")
    #
    #     self.update_sale_order_line_cost()
    #     self.add_new_products_to_sale_order()
    #
    #     revised_prices = False
    #     for line in self.product_summary_lines:
    #         if line.revised_unit_price != line.unit_price:
    #             revised_prices = True
    #             break
    #
    #     if revised_prices:
    #         # Get the salesperson from the related sale order
    #         sale_order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
    #         if sale_order:
    #             salesperson = sale_order.user_id
    #
    #             # Send an email to the salesperson
    #             if salesperson and salesperson.email:
    #                 mail_template = self.env.ref("purchase.email_template_revised_prices")
    #                 mail_template.send_mail(self.id, force_send=True, email_values={'email_to': salesperson.email})
    #                 # template = self.env.ref('purchase.model_purchase_order')
    #                 # template.send_mail(self.id, force_send=True, email_values={'email_to': salesperson.email})
    #
    #     return res

class PurchaseOrderProductSummary(models.Model):
    _name = 'purchase.order.product.summary'
    _description = 'Purchase Order Product Summary'

    sales_order_id = fields.Many2one('sale.order', string='Purchase Order', ondelete='cascade')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(related='product_id.name', string='Product Name', readonly=True)
    unit_price = fields.Float(related='product_id.standard_price', string='Unit Price', readonly=True)
    revised_unit_price = fields.Float(string='Revised Unit Price')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, readonly=True)
    related_sale_order_id = fields.Many2one('sale.order', related='purchase_order_id.related_sale_order_id', store=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'



    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        if 'price_unit' in vals:
            for line in self:
                product_summary_vals = {
                    'product_id': line.product_id.id,
                    'revised_unit_price': vals.get('price_unit'),
                }
                line.order_id.product_summary_lines += line.order_id.product_summary_lines.new(product_summary_vals)

                # Update the purchase_price field in the sale.order.line
                sale_order = self.env['sale.order'].search([('name', '=', line.order_id.origin)], limit=1)
                if sale_order:
                    sale_order_line = sale_order.order_line.filtered(lambda l: l.product_id == line.product_id)
                    if sale_order_line:
                        sale_order_line.purchase_price = vals.get('price_unit')

        return res




#working
    # def write(self, vals):
    #     res = super(PurchaseOrderLine, self).write(vals)
    #     if 'price_unit' in vals:
    #         for line in self:
    #             product_summary_vals = {
    #                 'product_id': line.product_id.id,
    #                 'revised_unit_price': vals.get('price_unit'),
    #             }
    #             line.order_id.product_summary_lines += line.order_id.product_summary_lines.new(product_summary_vals)
    #
    #             # Update the price_unit field in the sale.order.line
    #             sale_order_line = self.env['sale.order.line'].search([
    #                 ('order_id', '=', line.order_id.origin),
    #                 ('product_id', '=', line.product_id.id)
    #             ], limit=1)
    #             if sale_order_line:
    #                 sale_order_line.price_unit = vals.get('price_unit')
    #
    #     return res