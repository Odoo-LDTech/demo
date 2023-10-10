from odoo import models, fields, api, _
from datetime import datetime, timedelta, date




class RepairOrder(models.Model):
    _inherit = 'repair.order'

    type = fields.Selection([('internal', 'Internal'), ('external', 'External')], string='Type', store=True)

    @api.onchange('type')
    def _compute_read_only(self):
        if self.type:
            self.sale_order_id = None
            self.partner_id = None
            self.picking_id = None
            self.address_id = None

