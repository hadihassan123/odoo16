from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    supplier_price = fields.Float(
        string='Supplier Price',
        compute='_compute_supplier_price',
        inverse='_inverse_supplier_price',
        store=True
    )

    @api.depends('product_id', 'product_id.seller_ids.price')
    def _compute_supplier_price(self):
        for line in self:
            if line.product_id and line.product_id.seller_ids:
                line.supplier_price = min(line.product_id.seller_ids.mapped('price'))
            else:
                line.supplier_price = 0.0

    def _inverse_supplier_price(self):
        for line in self:
            if line.product_id and line.product_id.seller_ids:
                cheapest_supplier = min(line.product_id.seller_ids, key=lambda x: x.price)
                old_price = cheapest_supplier.price
                if old_price != line.supplier_price:  # Only update and log if there's a change
                    cheapest_supplier.price = line.supplier_price
                    self._log_price_change(line.product_id.product_tmpl_id, 'supplier_price', old_price,
                                           line.supplier_price)

    def _update_product_prices(self, vals):
        for line in self:
            if 'price_unit' in vals and line.product_id:
                old_price = line.product_id.list_price
                if old_price != vals['price_unit']:
                    line.product_id.list_price = vals['price_unit']
                    self._log_price_change(line.product_id.product_tmpl_id, 'list_price', old_price, vals['price_unit'])

            if 'purchase_price' in vals and line.product_id:
                old_price = line.product_id.standard_price
                if old_price != vals['purchase_price']:
                    line.product_id.standard_price = vals['purchase_price']
                    self._log_price_change(line.product_id.product_tmpl_id, 'standard_price', old_price, vals['purchase_price'])

    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        self._update_product_prices(vals)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleOrderLine, self).create(vals_list)
        for line, vals in zip(lines, vals_list):
            line._update_product_prices(vals)
        return lines

    def _log_price_change(self, product, field_changed, old_value, new_value):
        self.env['product.price.change.log'].create({
            'product_id': product.id,
            'field_changed': field_changed,
            'old_value': old_value,
            'new_value': new_value,
            'sale_order_line_id': self.id,
        })