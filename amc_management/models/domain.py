from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Domain(models.Model):
    _name = "amc.domain"
    _description = "amc domain"
    _rec_name = "category"

    category = fields.Char(string="Name")
    domain = fields.Many2one('amc.category', string="Domain", unique=True)
    active = fields.Boolean(default=True)
    category_test = fields.Selection([('network', 'NETWORK'), ('wireless', 'WIRELESS')])
    brand = fields.Char(string="Brand")

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     domain = [('partner_id', '=', self.partner_id.id)]
    #     order_ids = self.env['amc.customers'].search(domain).filtered(lambda r: r.status == 'live').ids
    #     return {'domain': {'order_id': [('id', 'in', order_ids)]}}
    #
    # @api.onchange('service_type')
    # def onchange_service_type(self):
    #     if self.service_type:
    #         amc_customers = self.env['amc.customers'].search([('con_type', '=', self.service_type)])
    #         partner_ids = amc_customers.mapped('partner_id')
    #         return {'domain': {'partner_id': [('id', 'in', partner_ids.ids)]}}
    #     else:
    #         return {'domain': {'partner_id': []}}


class Category(models.Model):
    _name = "amc.category"
    _description = "amc category"
    _rec_name = "amc_category"

    amc_category = fields.Char(string="Name")
    comments = fields.Char(string="Comments")
