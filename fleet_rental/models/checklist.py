# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CarRentalChecklist(models.Model):
    _name = 'car.rental.checklist'

    checklist_active = fields.Boolean(string="Disponible", default=True)
    checklist_number = fields.Many2one('car.rental.contract', string="Checklist Number")