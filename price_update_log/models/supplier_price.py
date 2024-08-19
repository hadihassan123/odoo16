# from odoo import models, fields, api
#
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     supplier_price = fields.Float(
#         string='Supplier Price',
#         compute='_compute_supplier_price',
#         inverse='_inverse_supplier_price',
#         store=True,
#         readonly=False,
#     )
#
#
#     @api.depends('product_id', 'product_id.seller_ids.price')
#     def _compute_supplier_price(self):
#         for line in self:
#             if line.product_id and line.product_id.seller_ids:
#                 line.supplier_price = min(line.product_id.seller_ids.mapped('price'))
#             else:
#                 line.supplier_price = 0.0
#
#     def _inverse_supplier_price(self):
#         for line in self:
#             if line.product_id and line.product_id.seller_ids:
#                 cheapest_supplier = min(line.product_id.seller_ids, key=lambda x: x.price)
#                 old_price = cheapest_supplier.price
#                 cheapest_supplier.price = line.supplier_price
#                 self._log_price_change(line.product_id.product_tmpl_id, 'supplier_price', old_price,
#                                        line.supplier_price)
#
#     def write(self, vals):
#         for line in self:
#             if 'price_unit' in vals:
#                 self._log_price_change(line.product_id.product_tmpl_id, 'list_price', line.product_id.list_price,
#                                        vals['price_unit'])
#
#             if 'purchase_price' in vals:
#                 self._log_price_change(line.product_id.product_tmpl_id, 'standard_price',
#                                        line.product_id.standard_price, vals['purchase_price'])
#
#         result = super(SaleOrderLine, self).write(vals)
#
#         for line in self:
#             if 'price_unit' in vals:
#                 line.product_id.product_tmpl_id.list_price = vals['price_unit']
#
#             if 'purchase_price' in vals:
#                 line.product_id.product_tmpl_id.standard_price = vals['purchase_price']
#
#         return result
#
#     def _log_price_change(self, product, field_changed, old_value, new_value):
#         self.env['product.price.supplier.log'].create({
#             'product_id': product.id,
#             'field_changed': field_changed,
#             'old_value': old_value,
#             'new_value': new_value,
#             'sale_order_line_id': self.id,
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
#
#
# class ProductSupplierInfo(models.Model):
#     _inherit = 'product.supplierinfo'
#
#     def write(self, vals):
#         for supplier_info in self:
#             if 'price' in vals:
#                 self._log_price_change(supplier_info, 'supplier_price', supplier_info.price, vals['price'])
#
#         return super(ProductSupplierInfo, self).write(vals)
#
#     def _log_price_change(self, supplier_info, field_changed, old_value, new_value):
#         self.env['product.price.supplier.log'].create({
#             'product_id': supplier_info.product_tmpl_id.id,
#             'field_changed': field_changed,
#             'old_value': old_value,
#             'new_value': new_value,
#             'supplier_id': supplier_info.partner_id.id,
#         })

from odoo import models, fields, api


from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_change_log_ids = fields.One2many('product.price.change.log', 'product_id', string='Price Change Logs')

    # def write(self, vals):
    #     return super(ProductTemplate, self).write(vals)
    def write(self, vals):
        # We'll only create logs if the context indicates it's from a sale order line
        if self.env.context.get('create_price_log'):
            for product in self:
                if 'list_price' in vals:
                    self._log_price_change(product, 'list_price', product.list_price, vals['list_price'])
                if 'standard_price' in vals:
                    self._log_price_change(product, 'standard_price', product.standard_price, vals['standard_price'])

        return super(ProductTemplate, self).write(vals)

    def _log_price_change(self, product, field_changed, old_value, new_value):
        if old_value != new_value:
            self.env['product.price.change.log'].create({
                'product_id': product.id,
                'field_changed': field_changed,
                'old_value': old_value,
                'new_value': new_value,
                'sale_order_line_id': self.env.context.get('sale_order_line_id'),
            })


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#         self._update_product_prices()
#         return res
#
#     def _update_product_prices(self):
#         for line in self.order_line:
#             product = line.product_id.product_tmpl_id
#             if line.price_unit != product.list_price:
#                 product._log_price_change('sale_price', product.list_price, line.price_unit, self.id)
#                 product.list_price = line.price_unit
#             if hasattr(line, 'purchase_price') and line.purchase_price != product.standard_price:
#                 product._log_price_change('cost', product.standard_price, line.purchase_price, self.id)
#                 product.standard_price = line.purchase_price

            # current_supplier_price = product.get_supplier_price()
            # if line.supplier_price != current_supplier_price:
            #     product._log_price_change('supplier_price', current_supplier_price, line.supplier_price, self.id)
            #     supplier_info = self.env['product.supplierinfo'].search([
            #         ('product_tmpl_id', '=', product.id),
            #         '|', ('product_id', '=', product.product_variant_id.id), ('product_id', '=', False)
            #     ], limit=1, order='sequence')
            #     if supplier_info:
            #         supplier_info.price = line.supplier_price
            #     else:
            #         self.env['product.supplierinfo'].create({
            #             'product_tmpl_id': product.id,
            #             'price': line.supplier_price,
            #         })