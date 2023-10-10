# -*- coding: utf-8 -*-
from odoo import fields, models, api


class  RejectRemark(models.TransientModel):
	_name = 'material.issue.reject.remark'
	_description = 'Reject remark Wizard'

	name = fields.Text('Remarks',required=True)


	def action_reject_remark(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['store.issue'].browse(int(active_id))
		rec.write({'rejected_remarks':self.name,'state':'rejected'})