from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        if self.price_unit != self._origin.price_unit:
            for line in self:
                self.env['product.price.log'].create({
                    'product_id': self.product_id.id,
                    'old_price': self._origin.price_unit,
                    'new_price': self.price_unit,
                    'purchase_order_id': self.order_id.id,
                    'po_number': line.order_id.name,
                    'vendor_id': line.order_id.partner_id.id,

            })

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_log_ids = fields.One2many('product.price.log', 'product_tmpl_id', string='Price Change Logs')# from odoo import models, fields, api
    sale_order_info = fields.One2many('sale.order.line', 'product_id', string='Sale Order Information', compute='_compute_sale_order_info')

    def write(self, vals):
        if 'list_price' in vals:
            for product in self:
                self.env['product.price.log'].create({
                    'product_id': product.id,
                    'old_price': product.list_price,
                    'new_price': vals['list_price'],
                })
        return super(ProductTemplate, self).write(vals)
#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     sale_order_info = fields.One2many('sale.order.line', 'product_id', string='Sale Order Information', compute='_compute_sale_order_info')
#
#     def _compute_sale_order_info(self):
#         for template in self:
#             sale_lines = self.env['sale.order.line'].search([
#                 ('product_id.product_tmpl_id', '=', template.id),
#                 ('state', 'in', ['sale', 'done'])
#             ])
#             template.sale_order_info = sale_lines
