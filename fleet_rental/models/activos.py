# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class EntidadMatricula(models.Model):
    _inherit = ['account.asset']

    vehiculo = fields.Many2one('fleet.vehicle',string="Vehiculo")
    aditamento = fields.Many2one('car.tools', string="Aditamento")