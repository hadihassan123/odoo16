from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_min_price_history = fields.One2many('product.price.log', compute='_compute_product_min_price_history', string='Product Minimum Price History')

    @api.depends('order_line.product_id')
    def _compute_product_min_price_history(self):
        for order in self:
            product_ids = order.order_line.mapped('product_id').ids
            min_prices = self.env['product.price.log'].search([
                ('product_id', 'in', product_ids)
            ]).sorted(lambda r: (r.product_id.id, r.new_price))

            # Keep only the minimum price entry for each product
            min_price_entries = self.env['product.price.log']
            for product_id in product_ids:
                product_entries = min_prices.filtered(lambda r: r.product_id.id == product_id)
                if product_entries:
                    min_price_entries += product_entries[0]

            order.product_min_price_history = min_price_entries