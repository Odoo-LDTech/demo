# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
import babel
from odoo import api, fields, models, tools, _




class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    is_late = fields.Boolean(string="Is late ")

