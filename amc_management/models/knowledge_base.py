from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MaintenanceKnowledgeBase(models.Model):
    _name = 'maintenance.knowledge.base'
    _description = 'Maintenance Knowledge Base'

    _rec_name = "customer_id"

    customer_id = fields.Many2one('maintenance.customers', string='Customer')
    amc_category_id = fields.Many2one('amc.category', string='Category')
    domain_id = fields.Many2one('amc.domain', string='Sub Category')
    device_type_id = fields.Many2one('amc.brand', string='Product')
    subject_des = fields.Char( related='product_id.subject_des', string='Subject')
    resolved_remarks = fields.Text(string='Resolution')
    knowledge_id = fields.Many2one('maintenance.knowledge.base.product', string='product knowledge')
    product_id = fields.Many2one('maintenance.knowledge.base.product', string="Product")
    pro_ids = fields.One2many('maintenance.knowledge.base.product', 'pro_id', string="pro_ids")
    # test_ids = fields.Many2many('maintenance.knowledge.base.product', string="test_ids", domain=[])
    test_ids = fields.Many2many('maintenance.knowledge.base.product', 'maintenance_kb_product_rel', 'kb_id',
                               'product_id', string="pro_ids", domain=[])
    # product_records = fields.One2many('maintenance.knowledge.base.product', 'customer_id', string='Product Records')
    product_records = fields.One2many('maintenance.knowledge.base.product', 'pro_id', string='Product Records')


    @api.onchange('device_type_id')
    def _onchange_device_type_id(self):
        if self.device_type_id:
            customer_records = self.env['maintenance.knowledge.base.product'].search([
                ('device_type_id', '=', self.device_type_id.brand)
            ])
            self.product_records = [(6, 0, customer_records.ids)]
        else:
            self.product_records = [(5, 0, 0)]
    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     if self.product_id:
    #         self.subject_des = self.product_id.subject_des
    #         self.resolved_remarks = self.product_id.description
    #     else:
    #         self.subject_des = False
    #         self.resolved_remarks = False

    # @api.onchange('amc_category_id', 'domain_id')
    # def _onchange_category_sub_category_id(self):
    #     domain = []
    #     if self.amc_category_id:
    #         domain.append(('amc_category_id', '=', self.amc_category_id.id))
    #     if self.domain_id:
    #         domain.append(('domain_id', '=', self.domain_id.id))
    #
    #     return {'domain': {'product_id': domain}}

    # @api.onchange('device_type_id')
    # def _onchange_device_type_id(self):
    #     if self.device_type_id:
    #         customer_records = self.env['maintenance.knowledge.base.product'].search(
    #             [('device_type_id', '=', self.device_type_id.brand)])
    #         if customer_records:
    #             self.subject_des = "\n".join(
    #                 record.subject_des or "" for record in customer_records if isinstance(record.subject_des, str))
    #             self.resolved_remarks = "\n".join(record.description or "" for record in customer_records if
    #                                               isinstance(record.description, str))
    #         else:
    #             self.subject_des = ""
    #             self.resolved_remarks = ""
    #
    #




