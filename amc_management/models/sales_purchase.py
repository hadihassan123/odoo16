

# models/sale_rfq_mapping.py
from odoo import models, fields

#To exclude the product added from purchase.order.line and exclude from total amount.To not effect margin
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the SO line.
#         """
#         for line in self:
#             if line.price_unit > 0.0:  # Exclude lines with price_unit set to 0.0
#                 price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#                 taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
#                 line.update({
#                     'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                     'price_total': taxes['total_included'],
#                     'price_subtotal': taxes['total_excluded'],
#                 })
#             else:
#                 line.update({
#                     'price_tax': 0.0,
#                     'price_total': 0.0,
#                     'price_subtotal': 0.0,
#                 })

class SaleOrder(models.Model):
    _inherit = 'sale.order'



    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
    #         if order_lines:
    #             rfq_vals = order._prepare_rfq_vals()
    #             rfq = self.env['purchase.order'].create(rfq_vals)
    #
    #             purchase_order_lines = []
    #             for line in order_lines:
    #                 purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
    #                 purchase_order_lines.append((0, 0, purchase_order_line_vals))
    #
    #             rfq.write({'order_line': purchase_order_lines})
    #
    #     return res
    def action_confirm(self):
        # Remove the line: res = super(SaleOrder, self).action_confirm()

        for order in self:
            order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
            if order_lines:
                vendors = {}
                for line in order_lines:
                    product = line.product_id
                    if product.seller_ids:
                        vendor_id = product.seller_ids[0].partner_id.id
                        if vendor_id not in vendors:
                            vendors[vendor_id] = []
                        vendors[vendor_id].append(line)

                for vendor_id, lines in vendors.items():
                    rfq_vals = order._prepare_rfq_vals(vendor_id)
                    rfq = self.env['purchase.order'].create(rfq_vals)

                    purchase_order_lines = []
                    for line in lines:
                        purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
                        purchase_order_lines.append((0, 0, purchase_order_line_vals))

                    rfq.write({'order_line': purchase_order_lines})
                    # _logger.info(f"RFQ {rfq.name} created for vendor {vendor_id} from Sale Order {order.name}")

        # Uncomment the line below if you want to call the parent method after your custom logic
        # return super(SaleOrder, self).action_confirm()

    # ... (the rest of the code remains the same)

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
    #         if order_lines:
    #             vendors = {}
    #             for line in order_lines:
    #                 product = line.product_id
    #                 if product.seller_ids:
    #                     vendor_id = product.seller_ids[0].partner_id.id
    #                     if vendor_id not in vendors:
    #                         vendors[vendor_id] = []
    #                     vendors[vendor_id].append(line)
    #
    #             for vendor_id, lines in vendors.items():
    #                 rfq_vals = order._prepare_rfq_vals(vendor_id)
    #                 rfq = self.env['purchase.order'].create(rfq_vals)
    #
    #                 purchase_order_lines = []
    #                 for line in lines:
    #                     purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
    #                     purchase_order_lines.append((0, 0, purchase_order_line_vals))
    #
    #                 rfq.write({'order_line': purchase_order_lines})
    #                 # _logger.info(f"RFQ {rfq.name} created for vendor {vendor_id} from Sale Order {order.name}")
    #
    #     return res

    def _prepare_rfq_vals(self, vendor_id):
        return {
            'partner_id': vendor_id,
            'date_order': self.date_order,
            'company_id': self.company_id.id,
            'origin': self.name,
            'payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
            'state': 'draft',  # RFQ state
        }

    def _prepare_purchase_order_line_vals(self, sale_order_line, rfq):
        product = sale_order_line.product_id
        price_unit = 0.0
        if product.seller_ids:
            price_unit = product.seller_ids[0].price or product.standard_price
        else:
            seller = product._select_seller(partner_id=self.partner_id)
            price_unit = seller.price or product.standard_price

        return {
            'name': sale_order_line.name,
            'product_id': product.id,
            'product_qty': sale_order_line.product_uom_qty,
            'product_uom': sale_order_line.product_uom.id,
            'price_unit': price_unit,
            'date_planned': sale_order_line.order_id.date_order,
            'order_id': rfq.id,
        }

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
    #         if order_lines:
    #             # Get the vendor for the first product in the order lines
    #             vendor = False
    #             if order_lines[0].product_id.seller_ids:
    #                 vendor = order_lines[0].product_id.seller_ids[0].partner_id.id
    #             if vendor:
    #                 rfq_vals = order._prepare_rfq_vals(vendor)
    #                 rfq = self.env['purchase.order'].create(rfq_vals)
    #
    #                 purchase_order_lines = []
    #                 for line in order_lines:
    #                     purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
    #                     purchase_order_lines.append((0, 0, purchase_order_line_vals))
    #
    #                 rfq.write({'order_line': purchase_order_lines})
    #
    #     return res
    #
    #
    #
    # def _prepare_rfq_vals(self, vendor_id):
    #     return {
    #         'partner_id': vendor_id,
    #         'date_order': self.date_order,
    #         'company_id': self.company_id.id,
    #         'origin': self.name,
    #         'payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
    #         'state': 'draft',  # RFQ state
    #     }
    #
    #
    # def _prepare_purchase_order_line_vals(self, sale_order_line, rfq):
    #     product = sale_order_line.product_id
    #     vendor = False
    #     price_unit = 0.0
    #     if product.seller_ids:
    #         vendor = product.seller_ids[0].partner_id
    #         price_unit = product.seller_ids[0].price or product.standard_price
    #     else:
    #         seller = product._select_seller(partner_id=self.partner_id)
    #         price_unit = seller.price or product.standard_price
    #
    #     return {
    #         'name': sale_order_line.name,
    #         'product_id': product.id,
    #         'product_qty': sale_order_line.product_uom_qty,
    #         'product_uom': sale_order_line.product_uom.id,
    #         'price_unit': price_unit,
    #         'date_planned': sale_order_line.order_id.date_order,
    #         'order_id': rfq.id,
    #     }




# models/sale_rfq_mapping.py
from odoo import models, fields

#To exclude the product added from purchase.order.line and exclude from total amount.To not effect margin
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the SO line.
#         """
#         for line in self:
#             if line.price_unit > 0.0:  # Exclude lines with price_unit set to 0.0
#                 price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#                 taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
#                 line.update({
#                     'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                     'price_total': taxes['total_included'],
#                     'price_subtotal': taxes['total_excluded'],
#                 })
#             else:
#                 line.update({
#                     'price_tax': 0.0,
#                     'price_total': 0.0,
#                     'price_subtotal': 0.0,
#                 })

class SaleOrder(models.Model):
    _inherit = 'sale.order'



    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
    #         if order_lines:
    #             rfq_vals = order._prepare_rfq_vals()
    #             rfq = self.env['purchase.order'].create(rfq_vals)
    #
    #             purchase_order_lines = []
    #             for line in order_lines:
    #                 purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
    #                 purchase_order_lines.append((0, 0, purchase_order_line_vals))
    #
    #             rfq.write({'order_line': purchase_order_lines})
    #
    #     return res

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
    #         if order_lines:
    #             vendors = {}
    #             for line in order_lines:
    #                 product = line.product_id
    #                 if product.seller_ids:
    #                     vendor_id = product.seller_ids[0].partner_id.id
    #                     if vendor_id not in vendors:
    #                         vendors[vendor_id] = []
    #                     vendors[vendor_id].append(line)
    #
    #             for vendor_id, lines in vendors.items():
    #                 rfq_vals = order._prepare_rfq_vals(vendor_id)
    #                 rfq = self.env['purchase.order'].create(rfq_vals)
    #
    #                 purchase_order_lines = []
    #                 for line in lines:
    #                     purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
    #                     purchase_order_lines.append((0, 0, purchase_order_line_vals))
    #
    #                 rfq.write({'order_line': purchase_order_lines})
    #                 # _logger.info(f"RFQ {rfq.name} created for vendor {vendor_id} from Sale Order {order.name}")
    #
    #     return res

    def _prepare_rfq_vals(self, vendor_id):
        return {
            'partner_id': vendor_id,
            'date_order': self.date_order,
            'company_id': self.company_id.id,
            'origin': self.name,
            'payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
            'state': 'draft',  # RFQ state
        }

    def _prepare_purchase_order_line_vals(self, sale_order_line, rfq):
        product = sale_order_line.product_id
        price_unit = 0.0
        if product.seller_ids:
            price_unit = product.seller_ids[0].price or product.standard_price
        else:
            seller = product._select_seller(partner_id=self.partner_id)
            price_unit = seller.price or product.standard_price

        return {
            'name': sale_order_line.name,
            'product_id': product.id,
            'product_qty': sale_order_line.product_uom_qty,
            'product_uom': sale_order_line.product_uom.id,
            'price_unit': price_unit,
            'date_planned': sale_order_line.order_id.date_order,
            'order_id': rfq.id,
        }

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
            if order_lines:
                # Get the vendor for the first product in the order lines
                vendor = False
                if order_lines[0].product_id.seller_ids:
                    vendor = order_lines[0].product_id.seller_ids[0].partner_id.id
                if vendor:
                    rfq_vals = order._prepare_rfq_vals(vendor)
                    rfq = self.env['purchase.order'].create(rfq_vals)

                    purchase_order_lines = []
                    for line in order_lines:
                        purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
                        purchase_order_lines.append((0, 0, purchase_order_line_vals))

                    rfq.write({'order_line': purchase_order_lines})

        return res

    #
    #
    # def _prepare_rfq_vals(self, vendor_id):
    #     return {
    #         'partner_id': vendor_id,
    #         'date_order': self.date_order,
    #         'company_id': self.company_id.id,
    #         'origin': self.name,
    #         'payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
    #         'state': 'draft',  # RFQ state
    #     }
    #
    #
    # def _prepare_purchase_order_line_vals(self, sale_order_line, rfq):
    #     product = sale_order_line.product_id
    #     vendor = False
    #     price_unit = 0.0
    #     if product.seller_ids:
    #         vendor = product.seller_ids[0].partner_id
    #         price_unit = product.seller_ids[0].price or product.standard_price
    #     else:
    #         seller = product._select_seller(partner_id=self.partner_id)
    #         price_unit = seller.price or product.standard_price
    #
    #     return {
    #         'name': sale_order_line.name,
    #         'product_id': product.id,
    #         'product_qty': sale_order_line.product_uom_qty,
    #         'product_uom': sale_order_line.product_uom.id,
    #         'price_unit': price_unit,
    #         'date_planned': sale_order_line.order_id.date_order,
    #         'order_id': rfq.id,
    #     }



#

#
# # models/sale_rfq_mapping.py
# from odoo import models, fields
#
# #To exclude the product added from purchase.order.line and exclude from total amount.To not effect margin
# # class SaleOrderLine(models.Model):
# #     _inherit = 'sale.order.line'
# #
# #     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
# #     def _compute_amount(self):
# #         """
# #         Compute the amounts of the SO line.
# #         """
# #         for line in self:
# #             if line.price_unit > 0.0:  # Exclude lines with price_unit set to 0.0
# #                 price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
# #                 taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
# #                 line.update({
# #                     'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
# #                     'price_total': taxes['total_included'],
# #                     'price_subtotal': taxes['total_excluded'],
# #                 })
# #             else:
# #                 line.update({
# #                     'price_tax': 0.0,
# #                     'price_total': 0.0,
# #                     'price_subtotal': 0.0,
# #                 })
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#
#     # def action_confirm(self):
#     #     res = super(SaleOrder, self).action_confirm()
#     #
#     #     for order in self:
#     #         purchase_order = self.env['purchase.order'].search([('origin', '=', order.name)], limit=1)
#     #         if purchase_order:
#     #             for purchase_line in purchase_order.order_line:
#     #                 if purchase_line.product_id not in order.order_line.mapped('product_id'):
#     #                     order_line_vals = {
#     #                         'product_id': purchase_line.product_id.id,
#     #                         'product_uom_qty': purchase_line.product_qty,
#     #                         'product_uom': purchase_line.product_uom.id,
#     #                         'price_unit': purchase_line.price_unit,
#     #                         'order_id': order.id,
#     #                     }
#     #                     self.env['sale.order.line'].create(order_line_vals)
#     #
#     #     return res
#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#
#         for order in self:
#             order_lines = order.order_line.filtered(lambda line: line.product_id.purchase_ok)
#             if order_lines:
#                 rfq_vals = order._prepare_rfq_vals()
#                 rfq = self.env['purchase.order'].create(rfq_vals)
#
#                 purchase_order_lines = []
#                 for line in order_lines:
#                     purchase_order_line_vals = order._prepare_purchase_order_line_vals(line, rfq)
#                     purchase_order_lines.append((0, 0, purchase_order_line_vals))
#
#                 rfq.write({'order_line': purchase_order_lines})
#
#         return res
#
#     def _prepare_rfq_vals(self):
#         partner = self.partner_id
#         if partner.parent_id and partner.parent_id.is_company:
#             partner = partner.parent_id
#         return {
#             'partner_id': partner.id,
#             'date_order': self.date_order,
#             'company_id': self.company_id.id,
#             'origin': self.name,
#             'payment_term_id': partner.property_supplier_payment_term_id.id,
#             'state': 'draft',  # RFQ state
#         }
#
#     def _prepare_purchase_order_line_vals(self, sale_order_line, rfq):
#         product = sale_order_line.product_id
#         seller = product._select_seller(partner_id=self.partner_id)
#         price_unit = seller.price or product.standard_price
#         return {
#             'name': sale_order_line.name,
#             'product_id': product.id,
#             'product_qty': sale_order_line.product_uom_qty,
#             'product_uom': sale_order_line.product_uom.id,
#             'price_unit': price_unit,
#             'date_planned': sale_order_line.order_id.date_order,
#             'order_id': rfq.id,
#         }
# # class SaleOrder(models.Model):
# #     _inherit = 'sale.order'
# #
# #     def action_confirm(self):
# #         res = super(SaleOrder, self).action_confirm()
# #         # Create Purchase Order
# #         PurchaseOrder = self.env['purchase.order']
# #         purchase_order_vals = {
# #             'partner_id': self.partner_id.id,
# #             # Add other necessary fields from the sale order to the purchase quotation
# #         }
# #         PurchaseOrder.create(purchase_order_vals)
# #         return res
# # # class SaleRfqMapping(models.Model):
# #     _name = 'sale.rfq.mapping'
# #     _description = 'Sale Order to RFQ Mapping'
# #
# #     sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
# #     rfq_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
# #
# # class SaleOrder(models.Model):
# #     _inherit = 'sale.order'
# #
# #     def action_confirm(self):
# #         res = super(SaleOrder,self).action_confirm()
# #         self.create_rfq()
# #         return res
# #
# #     def delete_record(self):
# #         for record in self:
# #             record.archive()
# #
# #     def create_rfq(self):
# #         rfq_env = self.env['purchase.order']
# #         rfq_line_env = self.env['purchase.requisition.line']
# #         mapping_env = self.env['sale.rfq.mapping']
# #
# #         for order in self:
# #             rfq = rfq_env.create({
# #                 'date_order': fields.Date.today(),
# #                 # 'user_id': self.env.user.id,
# #                 'partner_id': self.env.user.id,
# #
# #                 # Add other relevant fields from the sale order
# #             })
# #
# #             for line in order.order_line:
# #                 product = line.product_id
# #
# #                 rfq_line_env.create({
# #                     'requisition_id': rfq.id,
# #                     'product_id': product.id,
# #                     'product_qty': line.product_uom_qty,
# #                     'product_uom_id': line.product_uom.id,
# #                     # Add other relevant fields from the sale order line
# #                 })
# #
# #             mapping_env.create({
# #                 'sale_order_id': order.id,
# #                 'rfq_id': rfq.id,
# #             })
# #
# #         return True