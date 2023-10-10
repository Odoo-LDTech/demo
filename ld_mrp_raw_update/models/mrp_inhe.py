# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = 'stock.move'

    mrp_line_update = fields.Boolean(compute='_compute_mrp_line_update')

    def _compute_mrp_line_update(self):
        for rec in self:
            bom_id = rec.raw_material_production_id.bom_id
            bom_raw_primary_line = bom_id.bom_line_ids.filtered(lambda a: a.primary_raw)
            if rec.product_id == bom_raw_primary_line.product_id:
                rec.mrp_line_update = True
            else:
                rec.mrp_line_update = False


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    primary_raw = fields.Boolean('Primary Raw Material?')

    @api.onchange('primary_raw')
    def onchange_primary_raw(self):
        except_bom_line_ids = self._origin.bom_id.bom_line_ids.filtered(lambda a: a.id != self.id)
        except_bom_line_ids.primary_raw = False


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    primary_raw = fields.Boolean('Primary Raw Material?', compute='_compute_primary_raw')

    @api.onchange('bom_line_ids')
    def _compute_primary_raw(self):
        for rec in self:
            rec.primary_raw = self._origin.bom_line_ids.filtered(lambda a: a.primary_raw) or False


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    batch_order = fields.Boolean("Batch Order")

    @api.depends('bom_id', 'move_raw_ids')
    def _compute_product_qty(self):
        for production in self:
            if not production.batch_order or not production.bom_id.primary_raw:
                if production.state != 'draft':
                    continue
                if production.bom_id and production._origin.bom_id != production.bom_id:
                    production.product_qty = production.bom_id.product_qty
            else:

                bom_id = production.bom_id or production._origin.bom_id
                bom_id_end_qty = bom_id.product_qty
                # bom_line_min_id = bom_id.bom_line_ids.sorted(key=lambda r: r.product_qty)[0]
                bom_line_min_id = bom_id.bom_line_ids.filtered(lambda r: r.primary_raw)
                bom_line_min_qty = bom_line_min_id.product_qty

                move_raw_id = production.move_raw_ids.filtered(lambda z: z.product_id == bom_line_min_id.product_id)
                order_qty = move_raw_id.product_uom_qty

                if bom_line_min_qty <= order_qty:
                    if order_qty % bom_id_end_qty == 0:
                        production.product_qty = order_qty / bom_line_min_qty

                remain_ord_line_ids = production.move_raw_ids.filtered(lambda z: z.id != move_raw_id.id)

                for remain_line_id in remain_ord_line_ids:
                    res_bom_line_id = bom_id.bom_line_ids.filtered(lambda r: r.product_id == remain_line_id.product_id)
                    res_bom_line_qty = res_bom_line_id.product_qty
                    remain_line_id.product_uom_qty = production.product_qty * res_bom_line_qty
