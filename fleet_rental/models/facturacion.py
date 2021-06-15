# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FacturacionporVehiculo(models.Model):
    _inherit = ['account.move']

    renta = fields.Many2one('car.rental.contract,',string="Renta de Vehiculo")
    vehiculo = fields.Many2one('fleet.vehicle', string="Vehiculo")