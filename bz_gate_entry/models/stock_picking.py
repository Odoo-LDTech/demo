# # -*- coding: utf-8 -*-
# from odoo import SUPERUSER_ID, _, api, fields, models
#
#
# class Picking(models.Model):
#     _inherit = "stock.picking"
#     _description = "Transfer"
#
#     other_than_purchase = fields.Boolean(string='Other Than Purchase')
#     gate_id = fields.Many2one('gate.entry', string='Gate Entry', domain=[('entry_type', '=', 'other_purchase')])
#
#     @api.onchange('gate_id')
#     def _onchange_gate_id(self):
#         vals = []
#         if self.gate_id and self.gate_id.product_lines:
#             for line in self.gate_id.product_lines:
#                 dict = {
#                     'name': line.product_id.name,
#                     'picking_id': self.id,
#                     'location_dest_id': self.location_dest_id.id,
#                     'location_id': self.location_id.id,
#                     'picking_type_id': self.picking_type_id.id,
#                     'product_id': line.product_id.id,
#                     'product_uom_qty': line.quantity,
#                     'product_uom': line.product_id.uom_id.id
#                 }
#                 vals.append((0, 0, dict))
#             if vals:
#                 for move_line in self.move_ids_without_package:
#                     self.move_ids_without_package = [(2, move_line.id)]
#                 self.move_ids_without_package = vals
