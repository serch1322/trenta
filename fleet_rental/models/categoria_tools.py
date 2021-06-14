# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _

class toolscategory(models.Model):
    _name = 'tools.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Modelo", required=True)
    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)

class toolscategory(models.Model):
    _name = 'tools.categoria'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Categoria", required=True)
    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)