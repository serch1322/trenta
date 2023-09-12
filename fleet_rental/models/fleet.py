# -*- coding: utf-8 -*-

from odoo import models, fields


class FleetReservedTime(models.Model):
    _name = "rental.fleet.reserved"
    _description = "Reserved Time"

    customer_id = fields.Many2one('res.partner', string='Customer')
    date_from = fields.Date(string='Reserved Date From')
    date_to = fields.Date(string='Reserved Date To')
    reserved_obj = fields.Many2one('fleet.vehicle')

class ChecklistModelo(models.Model):
    _inherit = 'fleet.vehicle.model'

    linea_checklist = fields.One2many('linea.checklist', 'num_checklist', string="Checklist")

class LineaChecklist(models.Model):
    _name = 'linea.checklist'

    name = fields.Char(string="Nombre")
    num_checklist = fields.Many2one('fleet.vehicle.model',string="Número de Checklist")

class EmployeeFleet(models.Model):
    _inherit = 'fleet.vehicle'

    rental_check_availability = fields.Boolean(default=True, copy=False)
    rental_reserved_time = fields.One2many('rental.fleet.reserved', 'reserved_obj', string='Reserved Time', readonly=1,
                                           ondelete='cascade')







