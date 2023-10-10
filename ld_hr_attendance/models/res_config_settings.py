# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    grace_time = fields.Integer(string="Grace Time", readonly=False)

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param('ld_hr_attendance.grace_time', self.grace_time or 0)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['grace_time'] = self.env['ir.config_parameter'].sudo().get_param('ld_hr_attendance.grace_time')
        return res
