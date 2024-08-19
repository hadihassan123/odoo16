from odoo import models, fields, api

class ProductPriceUpdateLog(models.Model):
    _name = 'product.price.update.log'
    _description = 'Product Price Update Change Log'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now)
    field_changed = fields.Selection([
        ('sale_price', 'Sale Price'),
        ('cost', 'Cost'),
        ('supplier_price', 'Supplier Price')
    ], string='Field Changed')
    old_value = fields.Float(string='Old Value')
    new_value = fields.Float(string='New Value')
    description = fields.Text(string='Description')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_change_update_logs = fields.One2many('product.price.update.log', 'product_id', string='Price Update Logs')


    # def _log_price_change(self, field_changed, old_value, new_value, sale_order_id=False):
    #     self.ensure_one()
    #     self.env['product.price.update.log'].create({
    #         'product_id': self.id,
    #         'sale_order_id': sale_order_id,
    #         'field_changed': field_changed,
    #         'old_value': old_value,
    #         'new_value': new_value,
    #         'description': f"Changed {field_changed} from {old_value} to {new_value}"
    #     })
    def _log_price_change(self, field_changed, old_value, new_value, sale_order_id=False):
        self.ensure_one()
        product_id = self.product_variant_id.id if self._name == 'product.template' else self.id
        self.env['product.price.update.log'].create({
            'product_id': product_id,
            'sale_order_id': sale_order_id,
            'field_changed': field_changed,
            'old_value': old_value,
            'new_value': new_value,
            'description': f"Changed {field_changed} from {old_value} to {new_value}"
        })

    def write(self, vals):
        for product in self:
            if 'list_price' in vals:
                product._log_price_change('sale_price', product.list_price, vals['list_price'])
            if 'standard_price' in vals:
                product._log_price_change('cost', product.standard_price, vals['standard_price'])

            # Log supplier price changes
            old_supplier_price = product.get_supplier_price()
            result = super(ProductTemplate, product).write(vals)
            new_supplier_price = product.get_supplier_price()

            if old_supplier_price != new_supplier_price:
                product._log_price_change('supplier_price', old_supplier_price, new_supplier_price)

            return result

        return super(ProductTemplate, self).write(vals)


    def get_supplier_price(self):
        supplier_prices = {}
        for product in self:
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.id),
                '|', ('product_id', '=', product.product_variant_id.id), ('product_id', '=', False)
            ], limit=1, order='sequence')
            supplier_prices[product.id] = supplier_info.price if supplier_info else 0.0

        return supplier_prices[self.id] if len(self) == 1 else supplier_prices


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self._update_product_prices()
        return res

    def _update_product_prices(self):
        for line in self.order_line:
            product = line.product_id.product_tmpl_id
            if line.price_unit != product.list_price:
                product._log_price_change('sale_price', product.list_price, line.price_unit, self.id)
                product.list_price = line.price_unit
            if hasattr(line, 'purchase_price') and line.purchase_price != product.standard_price:
                product._log_price_change('cost', product.standard_price, line.purchase_price, self.id)
                product.standard_price = line.purchase_price

            current_supplier_price = product.get_supplier_price()
            if line.supplier_price != current_supplier_price:
                product._log_price_change('supplier_price', current_supplier_price, line.supplier_price, self.id)
                supplier_info = self.env['product.supplierinfo'].search([
                    ('product_tmpl_id', '=', product.id),
                    '|', ('product_id', '=', product.product_variant_id.id), ('product_id', '=', False)
                ], limit=1, order='sequence')
                if supplier_info:
                    supplier_info.price = line.supplier_price
                else:
                    self.env['product.supplierinfo'].create({
                        'product_tmpl_id': product.id,
                        'price': line.supplier_price,
                    })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    supplier_price = fields.Float(string='Supplier Price', compute='_compute_supplier_price',
                                  inverse='_inverse_supplier_price')

    @api.depends('product_id', 'product_id.seller_ids.price')
    def _compute_supplier_price(self):
        for line in self:
            if line.product_id and line.product_id.seller_ids:
                line.supplier_price = min(line.product_id.seller_ids.mapped('price'))
            else:
                line.supplier_price = 0.0

    def _inverse_supplier_price(self):
        for line in self:
            product = line.product_id.product_tmpl_id
            current_supplier_price = product.get_supplier_price()
            if line.supplier_price != current_supplier_price:
                product._log_price_change('supplier_price', current_supplier_price, line.supplier_price,
                                          line.order_id.id)
                supplier_info = self.env['product.supplierinfo'].search([
                    ('product_tmpl_id', '=', product.id),
                    '|', ('product_id', '=', line.product_id.id), ('product_id', '=', False)
                ], limit=1, order='sequence')
                if supplier_info:
                    supplier_info.price = line.supplier_price
                else:
                    self.env['product.supplierinfo'].create({
                        'product_tmpl_id': product.id,
                        'product_id': line.product_id.id,
                        'price': line.supplier_price,
                    })

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)  # Call the superclass method first
        if 'price_unit' in vals or 'standard_price' in vals:
            for line in self:
                product = line.product_id.product_tmpl_id

                if 'price_unit' in vals:
                    new_price = round(vals['price_unit'], 2)
                    old_price = round(product.list_price, 2)
                    if new_price != old_price:
                        product._log_price_change('sale_price', old_price, new_price, line.order_id.id)
                        product.list_price = new_price

                if 'standard_price' in vals:
                    new_cost = round(vals['standard_price'], 2)
                    old_cost = round(product.standard_price, 2)
                    if new_cost != old_cost:
                        product._log_price_change('cost', old_cost, new_cost, line.order_id.id)
                        product.standard_price = new_cost

        return res


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
#     def _log_price_change(self, field_changed, old_value, new_value, sale_order_id=False):
#         self.ensure_one()
#         product_id = self.product_variant_id.id if self._name == 'product.template' else self.id
#         self.env['product.price.update.log'].create({
#             'product_id': product_id,
#             'sale_order_id': sale_order_id,
#             'field_changed': field_changed,
#             'old_value': old_value,
#             'new_value': new_value,
#             'description': f"Changed {field_changed} from {old_value} to {new_value}"
#         })