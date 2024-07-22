from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import base64
from odoo.exceptions import UserError
from odoo.http import request
from io import BytesIO
import csv
import io
import base64

from odoo.tools import config
import os

from odoo import models, http



class KnowledgeBase(models.Model):
    _name = 'maintenance.knowledge.base.product'
    _description = 'Maintenance Knowledge Base'
    _rec_name = 'device_type_id'

    amc_category_id = fields.Many2one(related='customer_id.amc_category_id',string='Category')
    domain_id = fields.Many2one(related='customer_id.domain_id',string='Sub Category')
    device_type_id = fields.Many2one(related='customer_id.device_type_id',string='Product')
    subject_des = fields.Char(related='customer_id.subject_des',string='Subject')
    description = fields.Text(related='customer_id.description', string='Resolution')

    customer_id = fields.Many2one('maintenance.customers', string='Customer')
    pro_id = fields.Many2one('maintenance.knowledge.base', string='pro_id')
    ref = fields.Char(string="reference", default=lambda self: _('New'))

    # subject_resolution = fields.Text(compute='_compute_subject_resolution', string='Subject Resolution')
    #
    # @api.depends('maintenance.knowledge.base')
    # def _compute_subject_resolution(self):
    #     for record in self:
    #         linked_record = self.env['maintenance.knowledge.base'].browse(record.id)
    #         if linked_record:
    #             record.subject_resolution = linked_record.subject_resolution

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('maintenance.knowledge.base.product')
        return super(KnowledgeBase, self).create(vals_list)
