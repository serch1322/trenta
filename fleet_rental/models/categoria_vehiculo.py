# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _

class CarCategory(models.Model):
    _name = 'car.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Categoria", required =True)
    conteo_vehiculo = fields.Integer(string="# Vehiculos", compute='conteo_de_vehiculos')
    tipo = fields.Selection([('utilitario', 'Utilitario'), ('carga', 'Carga')], string="Tipo de Vehiculo", copy=False)
    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)
    diario = fields.Many2one('account.journal', string="Diario", required=True, domain="[('type', '=', 'general'),('company_id', '=', company_id)]")



    def conteo_de_vehiculos(self):
        conteo = self.env['fleet.vehicle']
        for record in self:
            record.conteo_vehiculo = conteo.search_count([('categoria','=',record.id)])


    def abrir_vehiculos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehiculos',
            'view_mode': 'tree',
            'res_model': 'fleet.vehicle',
            'domain': [('categoria', '=', self.id)],
        }