from odoo import models, fields, api, _

# import re

from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pan_no = fields.Char(string="PAN No")
    pf_no = fields.Char(string="PF No")
    esi_no = fields.Char(string="ESI No")
    uan = fields.Char(string="UAN")
    last_app_dt = fields.Date(string="Last Appraisal Date")
    employee_id = fields.Char(string="Employee ID")

    @api.onchange('pan_no')
    def set_upper(self):
        if self.pan_no:
            self.pan_no = self.pan_no.upper()
        return

    @api.constrains('pan_no')
    def is_valid_pan_no(self):
        for data in self:
            if data.pan_no and len(data.pan_no) != 10:
                raise UserError(_("Values not sufficient !.. Please Enter 10 digit 'PAN' Number"))
            pan_no = self.env['hr.employee'].search([('pan_no', '=', data.pan_no), ('id', '!=', data.id),
                                                     ('pan_no', '!=', False), ('pan_no', '!=', '')])

            if pan_no:
                raise UserError(_('PAN No already exists for "%s" , Please enter the correct no.' % pan_no.name))

            if data.pan_no and not data.pan_no[0:5].isalpha():
                raise UserError(_("First five values of PAN no should be alphabet"))
            if data.pan_no and not data.pan_no[9].isalpha():
                raise UserError(_("Last value of PAN no should be alphabet"))
            if data.pan_no and not data.pan_no[5:9].isdigit():
                raise UserError(_("PAN no values from 5 to 8 Should be Integer"))

    
