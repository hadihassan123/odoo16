from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_field = fields.Many2one('sale.order',string ='custom field')
    contract_test = fields.Char(string="Contract label")
    amc_amount = fields.Integer(string="AMC Fee")

    @api.model
    def create(self, values):
        # Call the original create method
        sale_order = super(SaleOrder, self).create(values)


        if sale_order.confirm_amc =='yes' or sale_order.amc_included:
            partner_id = sale_order.partner_id.id
            name = sale_order.name
            status = sale_order.status
            po_date = sale_order.date_order
            contract_name = sale_order.contract_name
            contract_test = sale_order.contract_test
            amc_amount= sale_order.amc_amount
            amc_fee= sale_order.amc_fee


        else:
            return super(SaleOrder, self).create(values)



        amc_customers = self.env['amc.customers']
        amc_customers.create({
            'partner_id': partner_id,
            'name': name,
            'status': status,
            'po_date':po_date,
            'contract_name': contract_name,
            'contract_test': contract_test,
            'amc_amount': amc_amount,
            'amc_fee':amc_fee


        })

        return sale_order