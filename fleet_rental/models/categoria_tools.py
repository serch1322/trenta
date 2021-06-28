# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _

class ToolsModelo(models.Model):
    _name = 'tools.modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Modelo", required=True)
    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)
    diario = fields.Many2one('account.journal', string="Diario", required=True, domain="[('type', '=', 'general')]")
    conteo_aditamento = fields.Integer(string="# Vehiculos", compute='conteo_de_aditamento')

    def conteo_de_aditamento(self):
        conteo = self.env['car.tools']
        for record in self:
            record.conteo_aditamento = conteo.search_count([('modelo','=',record.id)])


    def abrir_aditamentos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Aditamentos/Accesorios',
            'view_mode': 'tree',
            'res_model': 'car.tools',
            'domain': [('modelo', '=', self.id)],
        }

class ToolsCategoria(models.Model):
    _name = 'tools.categoria'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Categoria", required=True)
    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)
    diario = fields.Many2one('account.journal', string="Diario", required=True, domain="[('type', '=', 'general')]")
    conteo_aditamento = fields.Integer(string="# Vehiculos", compute='conteo_de_aditamento')

    def conteo_de_aditamento(self):
        conteo = self.env['car.tools']
        for record in self:
            record.conteo_aditamento = conteo.search_count([('categoria', '=', record.id)])

    def abrir_aditamentos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Aditamentos/Accesorios',
            'view_mode': 'tree',
            'res_model': 'car.tools',
            'domain': [('categoria', '=', self.id)],
        }