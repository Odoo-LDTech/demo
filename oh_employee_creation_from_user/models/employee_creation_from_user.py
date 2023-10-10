# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee',
                                  string='Related Employee', ondelete='restrict', auto_join=True,
                                  help='Employee-related data of the user')

    @api.model
    def create(self, vals):
        """This code is to create an employee while creating an user."""

        result = super(ResUsersInherit, self).create(vals)
        # if not result.env.context.get('user_create'):
        #     employee_rec = self.env['hr.employee'].search([('name', '=', result['name'])], limit=1)
        #     if employee_rec:
        #         employee_rec.sudo().write({
        #             'user_id': result['id'],
        #             'address_home_id': result['partner_id'].id,
        #             'work_email': result.email})
        #     if not employee_rec:
        #         result['employee_id'] = self.env['hr.employee'].sudo().create({'name': result['name'],
        #                                                                        'user_id': result['id'],
        #                                                                        'address_home_id': result[
        #                                                                            'partner_id'].id,
        #                                                                        'work_email': result.email})
        return result

    def create_employee(self):
        for rec in self:
            employee_rec = self.env['hr.employee'].search([('name', '=', rec.name)], limit=1)
            if employee_rec:
                employee_rec.sudo().write({
                    'user_id': rec.id,
                    'address_home_id': rec.partner_id.id,
                    'work_email': rec.email})
            if not employee_rec:
                result = self.env['hr.employee'].sudo().create({'name': rec.name,
                                                               'user_id': rec.id,
                                                               'address_home_id': rec.partner_id.id,
                                                               'work_email': rec.email})

                return result


class Employee(models.Model):
    _inherit = 'hr.employee'

    user_create = fields.Boolean(string="user created by auto")

    def create_user(self):
        if not self.work_email:
            raise ValidationError(_('Please enter workemail'))
        usr_vals = {
            'name': self.name,
            'login': self.work_email,
            'email': self.work_email,
            'password': 123,
        }
        job_obj = self.env['hr.job']
        usr_obj = self.env['res.users']
        user = usr_obj.sudo().with_context(user_create=True).create(usr_vals)
        self.user_id = user.id
        return user
