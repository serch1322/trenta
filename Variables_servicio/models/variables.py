# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _name = 'variables.procesos'

    name = fields.Char(string="Variable de Proceso")
    precio = fields.Float(string='Precio',store=True,default=0.0)
