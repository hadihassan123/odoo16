from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Eng(models.Model):
    _name = "eng.domain"
    _description = "eng domain"
    _rec_name = "eng_name_eng_dept"

    eng_name = fields.Char(string="Engineer's name")
    eng_dept = fields.Char(string="Department")

    @api.depends('eng_name', 'eng_dept')
    def _compute_eng_name_eng_dept(self):
        for record in self:
            record.eng_name_eng_dept = f"{record.eng_name} - {record.eng_dept}"

    eng_name_eng_dept = fields.Char(compute='_compute_eng_name_eng_dept', string="Name & Department", store=True)

