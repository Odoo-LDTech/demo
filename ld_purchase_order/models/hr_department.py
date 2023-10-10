from odoo import api, fields, models, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class hr_department(models.Model):
    _inherit = 'hr.department'


    store_manager_id = fields.Many2one('hr.employee',string="Store Manager")