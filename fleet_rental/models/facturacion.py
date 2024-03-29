# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FacturacionporRenta(models.Model):
    _inherit = ['account.move']

    renta = fields.Many2one('car.rental.contract',string="Renta de Vehiculo", store=True, copy=False)
    inicio = fields.Date(string="Periodo Inicio", readonly=True)
    fin = fields.Date(string="Periodo Final", readonly=True)
    sucursal = fields.Many2one('res.partner',string="Centro de Negocio",store=True)

class FacturacionporVehiculo(models.Model):
    _inherit = ['account.move.line']

    vehiculo = fields.Many2one('fleet.vehicle',string="Vehiculo",readonly=True,store=True,copy=False)
    aditamento = fields.Many2one('car.tools',string="Aditamentos/Accesorios",readonly=True,store=True,copy=False)