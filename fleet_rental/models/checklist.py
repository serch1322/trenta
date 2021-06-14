# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CarRentalChecklist(models.Model):
    _name = 'car.rental.checklist'

    name = fields.Many2one('car.tools', string="Accesorio")
    checklist_active = fields.Boolean(string="Disponible", default=True)
    checklist_number = fields.Many2one('car.rental.contract', string="Checklist Number")
    num_serie = fields.Char(string="Número de Serie")
    price = fields.Float(string="Precio")


    @api.onchange('name')
    def onchange_name(self):
        self.price = self.name.rent_price
        self.num_serie = self.name.num_serie

    def _poner_tools(self):
        self.ensure_one()
        servicio = self.env['car.rental.contract']
        valores_servicio = {}
        if self.name.car == servicio.vehicle_id:
            valores_servicio.update({
                'name': self.name.id,
            })
        servicio_creado = servicio.write(valores_servicio)