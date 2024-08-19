# from odoo import models, fields, api
#
# class ProductPriceChangeLog(models.Model):
#     _name = 'product.price.supplier.log'
#     _description = 'Product Price Updation Log'
#     _order = 'date desc'
#
#     product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
#     date = fields.Datetime(string='Change Date', default=fields.Datetime.now, required=True)
#     field_changed = fields.Selection([
#         ('list_price', 'Sales Price'),
#         ('standard_price', 'Cost'),
#         ('supplier_price', 'Supplier Price')
#     ], string='Field Changed')
#     old_value = fields.Float(string='Old Value')
#     new_value = fields.Float(string='New Value')
#     user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
#     sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
#     supplier_id = fields.Many2one('res.partner', string='Supplier')
#     sale_order_id = fields.Many2one('sale.order', string='Sale Order')
#     description = fields.Text(string='Description')
#
#
#
#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     price_change_supplier_ids = fields.One2many('product.price.supplier.log', 'product_id', string='Price Change Logs')
#
#     # def write(self, vals):
#     #     for product in self:
#     #         if 'list_price' in vals:
#     #             self._log_price_change(product, 'list_price', product.list_price, vals['list_price'])
#     #         if 'standard_price' in vals:
#     #             self._log_price_change(product, 'standard_price', product.standard_price, vals['standard_price'])
#     #
#     #     return super(ProductTemplate, self).write(vals)
#
#     def write(self, vals):
#         for product in self:
#                 if 'list_price' in vals:
#                     product._log_price_change('sale_price', product.list_price, vals['list_price'])
#                 if 'standard_price' in vals:
#                     product._log_price_change('cost', product.standard_price, vals['standard_price'])
#
#     def _log_price_change(self, product, field_changed, old_value, new_value):
#         self.env['product.price.supplier.log'].create({
#             'product_id': product.id,
#             'field_changed': field_changed,
#             'old_value': old_value,
#             'new_value': new_value,
#         })
#
#     # def _log_price_change(self, field_changed, old_value, new_value, sale_order_id=False):
#     #     self.ensure_one()
#     #     product_id = self.product_variant_id.id if self._name == 'product.template' else self.id
#     #     self.env['product.price.supplier.log'].create({
#     #         'product_id': product_id,
#     #         'sale_order_id': sale_order_id,
#     #         'field_changed': field_changed,
#     #         'old_value': old_value,
#     #         'new_value': new_value,
#     #         'description': f"Changed {field_changed} from {old_value} to {new_value}"
#     #     })
from odoo import models, fields, api

class ProductPriceChangeLog(models.Model):
    _name = 'product.price.change.log'
    _description = 'Product Price Change Log'
    _order = 'date desc'

    product_id = fields.Many2one('product.template', string='Product', required=True)
    date = fields.Datetime(string='Change Date', default=fields.Datetime.now, required=True)
    field_changed = fields.Selection([
        ('list_price', 'Sales Price'),
        ('standard_price', 'Cost'),
        ('supplier_price', 'Supplier Price')
    ], string='Changed Field', required=True)
    old_value = fields.Float(string='Old Value')
    new_value = fields.Float(string='New Value')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')