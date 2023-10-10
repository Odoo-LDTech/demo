from odoo import models, fields, api, _
from datetime import datetime, timedelta, date


class GateEntry(models.Model):
    _name = "gate.entry"
    _inherit = ['mail.thread']
    _order = "name desc"

    def _get_employee_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_id.id

    def compute_arrival_gap(self):
        for record in self:
            arrival_gap = 0
            if record.po_number.picking_ids and record.entry_date:
                for picking in record.po_number.picking_ids:
                    if picking.picking_type_code == 'incoming' and picking.date_done:
                        diff = picking.date_done - record.entry_date
                        days, seconds = diff.days, diff.seconds
                        arrival_gap = days * 24 + seconds // 3600
                        break
            record.arrival_gap = arrival_gap

    name = fields.Char('Name', index=True, default=lambda self: _('New'))
    remark = fields.Char(string='Remark')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, default=_get_employee_id,
                                  track_visibility='onchange')
    date = fields.Date(string='Date', readonly=True, default=datetime.today())
    driver_name = fields.Char('Driver Name')
    vehicle_number = fields.Char('Vehicle Number')
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate')],
                             string='Status', required=True, default='draft')
    entry_type = fields.Selection(
        [('purchase', 'Purchase / Inward'), ('non_purchase', 'NonPurchase'), ('outward', 'Outward')],
        string='Entry Type', required=True)
    po_number = fields.Many2one('purchase.order', string='PO Number', domain=[('state', '=', 'purchase')])
    # inbound_number = fields.Many2one('vehicle.inbound', string='Inward Number')
    # name1 = fields.Many2one('vehicle.outbound', string='Outbound Number')
    booked_by = fields.Char(string='Booked By')
    driver_mob_no = fields.Char(string='Driver Mobile No')
    contact_person = fields.Char('Contact Person')
    location_point = fields.Char('Location Point')
    odometer_starting = fields.Float(string='Starting Odometer')
    odometer_ending = fields.Float(string='Ending Odometer')
    in_date = fields.Datetime(string='In Date')
    out_date = fields.Datetime(string='Out Date')
    entry_date = fields.Datetime(string='Entry Datetime')
    arrival_date = fields.Datetime(string='Arrival Time Gap')
    arrival_gap = fields.Float(string="Arrival Time Gap (Hours)", compute='compute_arrival_gap')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    product_lines = fields.One2many('gate.entry.line', 'entry_id', string='Payslips')
    # picking_ids = fields.Many2many('stock.picking', string='Receipts')
    supplier_id = fields.Many2one("res.partner", string="Supplier Name")
    reason_entry = fields.Text(string="Reason for Pass")
    supervisior_id = fields.Many2one("res.partner", string="Grade / Supervisor Name")
    from_h = fields.Char(string="From")
    state_h = fields.Char(string="State")
    seal_no = fields.Char(string="Seal No.")

    @api.model
    def create(self, vals):
        current_year = datetime.now().year
        today = date.today()
        start_year = date(current_year, 4, 1)
        if today > start_year:
            gate_entry = self.search([('create_date', '>', start_year)])
            seq_gate_entry_with_date = self.env.ref('bz_gate_entry.seq_gate_entry_with_date')
            if not gate_entry:
                seq_gate_entry_with_date.sudo().write({
                    'number_next_actual': 1
                })

        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('gate.entry.date') or _('New')
            month = datetime.today().month
            year = str(datetime.today().year)[2:]
            if month < 10:
                month = '0' + str(month)
            else:
                month = str(month)
            vals['name'] = 'GT/' + month + '/' + year + '/' + seq
        result = super(GateEntry, self).create(vals)
        return result

    def action_validate(self):
        for data in self:
            # data.update({'picking_ids': [(6, 0, self.po_number.picking_ids.ids)]})
            data.state = 'validate'

    @api.onchange('entry_type')
    def onchange_entry_type(self):
        self.driver_name = None
        self.driver_mob_no = None
        self.vehicle_number = None
        self.booked_by = None
        self.contact_person = None
        self.location_point = None
        self.odometer_starting = None
        self.out_date = None
        # self.inbound_number = None
        # self.name1 = None
        self.in_date = None
        self.odometer_ending = None

    @api.onchange('po_number')
    def onchange_po_number(self):
        for rec in self.po_number:
            # update new record
            po_obj = rec._origin
            if po_obj.order_line:
                for product_line in self.product_lines:
                    self.product_lines = [(2, product_line.id)]
            for line in po_obj.order_line:
                product_line = {
                    'product_barcode': line.barcode_scan,
                    'product_id': line.product_id.id,
                    'uom_id': line.product_uom,
                    'quantity': line.product_qty,
                    'po_id': po_obj.id
                }
                self.write({
                    'product_lines': [(0, 0, product_line)]
                })

    @api.onchange('inbound_number')
    def onchange_inbound_number(self):
        for rec in self.inbound_number:
            inbound_obj = rec._origin

            self.driver_name = self.inbound_number.driver_name.name
            self.driver_mob_no = self.inbound_number.driver_name.mobile
            self.vehicle_number = self.inbound_number.vehicle_number.license_plate
            self.booked_by = self.inbound_number.booked_by
            self.contact_person = self.inbound_number.contact_person
            self.location_point = self.inbound_number.location_point
            self.odometer_starting = self.inbound_number.odometer_starting
            self.out_date = self.inbound_number.out_date

    @api.onchange('name1')
    def onchange_name1(self):
        for rec in self.name1:
            outbound_obj = rec._origin

            print(outbound_obj.driver_id)
            print(outbound_obj.vehicle_number)
            self.driver_name = self.name1.driver_id.name
            self.driver_mob_no = self.name1.driver_id.mobile
            self.vehicle_number = self.name1.vehicle_number.license_plate
            self.booked_by = self.name1.booked_by
            self.contact_person = self.name1.contact_person
            self.location_point = self.name1.container_drop_point
            self.odometer_starting = self.name1.odometer_starting
            self.out_date = self.name1.out_date


class GateEntryLine(models.Model):
    _name = "gate.entry.line"

    entry_id = fields.Many2one('gate.entry', string='Entry')
    product_barcode = fields.Char('Barcode')
    product_id = fields.Many2one('product.product', string='Product')
    po_id = fields.Integer('PO Id')
    quantity = fields.Float('Quantity')
    # abw_gm = fields.Char(string="ABW GM")
    # count = fields.Char(string="Count")
    # grade = fields.Char(string="Grade")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")


# class Picking(models.Model):
#     _inherit = "stock.picking"
#
#     def compute_gate_count(self):
#         for record in self:
#             record.gate_entry_count = self.env['gate.entry'].search_count([('picking_ids', '=', record.id)])
#
#     def compute_gate_pass(self):
#         for record in self:
#             gate_entry = self.env['gate.entry'].search([('picking_ids', '=', record.id)], limit=1)
#             if gate_entry:
#                 record.gate_pass = gate_entry.name
#             else:
#                 record.gate_pass = ''
#
#     gate_entry_count = fields.Integer('Gate Entry', compute='compute_gate_count')
#     gate_pass = fields.Char(string="Gate Pass Number", compute='compute_gate_pass')
#
#     def get_gate_entry(self):
#         """Gate entry smart button"""
#         self.ensure_one()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Gate Entry',
#             'view_mode': 'tree,form',
#             'res_model': 'gate.entry',
#             'domain': [('picking_ids', '=', self.id)],
#             'context': "{'create': False}"
#         }
#
#     transportaion_details_ids = fields.One2many("transportation.details.line", "line_id")
#     plant_count_ids = fields.One2many("plant.count.line", "count_id")
#     plant_real_weight_total = fields.Float(string="Real Weight Total", compute="_get_real_weight_total", store=True)
#     from_h = fields.Char(string="From")
#     state_h = fields.Many2one("res.country.state", string="State")
#     seal_no = fields.Char(string="Seal No.")
#     count_transportaion = fields.Boolean(string='Count Transportaion', store=True, compute='_count_transportaion')
#
#     @api.depends('plant_count_ids.real_weight')
#     def _get_real_weight_total(self):
#         for rec in self:
#             total = 0.0
#             for weight in rec.plant_count_ids:
#                 total += weight.real_weight
#             rec.update({
#                 "plant_real_weight_total": total
#             })
#
#     @api.depends('transportaion_details_ids')
#     def _count_transportaion(self):
#         for rec in self:
#             count_transportaion = len(rec.transportaion_details_ids)
#             if count_transportaion > 1:
#                 rec.count_transportaion = True
#             else:
#                 rec.count_transportaion = False
#
#     def write(self, values):
#         res = super(Picking, self).write(values)
#         if self.plant_count_ids:
#             count = 1
#             for plan_line in self.plant_count_ids:
#                 plan_line.sudo().write({
#                     'crate': 'Crate ' + str(count)
#                 })
#                 count += 1
#         return res
#
#     def create(self, values):
#         res = super(Picking, self).create(values)
#         if res.plant_count_ids:
#             count = 1
#             for plan_line in res.plant_count_ids:
#                 plan_line.sudo().write({
#                     'crate': 'Crate ' + str(count)
#                 })
#                 count += 1
#         return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    abw_gm = fields.Char(string="ABW GM")
    count = fields.Char(string="Count")
    grade = fields.Char(string="Grade")


class TransportaionDetailsLine(models.Model):
    _name = 'transportation.details.line'

    line_id = fields.Many2one("stock.picking")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle Number")
    driver = fields.Char(string="Driver")
    driver_contact = fields.Char(string="Driver Contact")
    packaging_type = fields.Selection([('crate', 'Crate'),
                                       ('empty_crate', 'Empty Crate'),
                                       ('ice_crate', 'Ice Crate'),
                                       ('container', 'Container'),
                                       ('box', 'Box')], string='Packaging Type')
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one("uom.uom", string="UOM")
    product_quantity = fields.Float(string="Product Quantity")
    product_uom_id = fields.Many2one("uom.uom", string="Product UOM")


class PlantCountLine(models.Model):
    _name = 'plant.count.line'

    count_id = fields.Many2one("stock.picking")
    crate = fields.Char(string="Add a Crate")
    full_weight = fields.Float(string="Filled Up Weight")
    full_uom_id = fields.Many2one("uom.uom", string="UOM")
    empty_weight = fields.Float(string="Empty Weight")
    empty_uom_id = fields.Many2one("uom.uom", string="UOM")
    real_weight = fields.Float(string="Real Weight", compute="_get_real_weight", store=True)
    real_uom_id = fields.Many2one("uom.uom", string="UOM")

    @api.depends("full_weight", "empty_weight")
    def _get_real_weight(self):
        for rec in self:
            rec.real_weight = rec.full_weight - rec.empty_weight
