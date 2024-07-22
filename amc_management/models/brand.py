from datetime import date, datetime,timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class Brand(models.Model):
    _name = "amc.brand"
    _description = " amc brand"
    _rec_name = "brand"

    brand = fields.Char(string='device type')
    domain_id = fields.Many2one('amc.domain', string='sub category')