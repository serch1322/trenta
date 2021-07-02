# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Venta(models.TransientModel):
    _name = 'venta.vehiculo'

    name = fields.Many2one('fleet.vehicle', string="Vehiculo", required=True)

    def vender_vehiculo(self):
        variable = self._context
        venta = self.env['fleet.vehicle'].browse(variable['active_id'])
        venta.vehicle_id = self.name.id
        return True