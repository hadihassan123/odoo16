from odoo import models, fields, api

class ProductPriceLog(models.Model):
    _name = 'product.price.log'
    _description = 'Product Price Change Log'
    _order = 'date desc'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', related='product_id.product_tmpl_id', store=True)
    old_price = fields.Float(string='Old Price')
    new_price = fields.Float(string='New Price')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    date = fields.Datetime(string='Change Date', default=fields.Datetime.now)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    name = fields.Char(related='purchase_order_id.name')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    po_number = fields.Char(string='PO Number')