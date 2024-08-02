from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    storable_product_total = fields.Float(string="Storable Products Total", compute="_compute_segregated_summary")
    storable_product_cost = fields.Float(string="Storable Products Cost", compute="_compute_segregated_summary")
    storable_product_margin = fields.Float(string="Storable Products Margin", compute="_compute_segregated_summary")

    service_total = fields.Float(string="Services Total", compute="_compute_segregated_summary")
    service_cost = fields.Float(string="Services Cost", compute="_compute_segregated_summary")
    service_margin = fields.Float(string="Services Margin", compute="_compute_segregated_summary")

    total_margin = fields.Float(string="Total Margin", compute="_compute_segregated_summary")
    total_cost = fields.Float(string="Total Cost", compute="_compute_segregated_summary")

    @api.depends('order_line.product_id', 'order_line.price_subtotal', 'order_line.product_uom_qty')
    def _compute_segregated_summary(self):
        for order in self:
            storable_lines = order.order_line.filtered(lambda l: l.product_id.type == 'consu')
            service_lines = order.order_line.filtered(lambda l: l.product_id.type == 'service')

            order.storable_product_total = sum(storable_lines.mapped('price_subtotal'))
            order.storable_product_cost = sum(storable_lines.mapped(lambda l: l.product_id.standard_price * l.product_uom_qty))
            order.storable_product_margin = order.storable_product_total - order.storable_product_cost

            order.service_total = sum(service_lines.mapped('price_subtotal'))
            order.service_cost = sum(service_lines.mapped(lambda l: l.product_id.standard_price * l.product_uom_qty))
            order.service_margin = order.service_total - order.service_cost

            order.total_margin = order.storable_product_margin + order.service_margin
            order.total_cost = order.storable_product_cost + order.service_cost