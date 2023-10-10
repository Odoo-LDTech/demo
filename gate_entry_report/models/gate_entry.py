from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
import calendar
from datetime import datetime, timedelta


class GateEntry(models.Model):
    _inherit = 'gate.entry'

    actual_in_time = fields.Char(string="Actual In Time", compute='_amount_in_time')
    actual_out_time = fields.Char(string="Actual out Time", compute='_amount_in_time')
    running_count = fields.Char(string="Running Count", compute='_amount_in_time')

    def _amount_in_time(self):
        for rec in self:
            if rec.odometer_ending:
                self.running_count = rec.odometer_ending - rec.odometer_starting
            else:
                rec.running_count = "-"
            if rec.in_date:
                date_format_in = rec.in_date
                date_field_in = date_format_in + timedelta(hours=5, minutes=30)
                self.actual_in_time = date_field_in

            else:
                rec.actual_in_time = "-"

            if rec.out_date:
                date_format_out = rec.out_date
                date_field_out = date_format_out + timedelta(hours=5, minutes=30)
                self.actual_out_time = date_field_out
            else:
                rec.actual_out_time = "-"
