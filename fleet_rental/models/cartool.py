# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CarTools(models.Model):
    _name = 'car.tools'
    _description = 'Accesorios/Aditamentos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", required=True)
    num_eco = fields.Char(string="Número Económico", copy=False, index=True, readonly=True)
    num_serie = fields.Char(string="Número de Serie")
    costo = fields.Float(string="Costo")
    state = fields.Selection([('almacen','Almacén'),('disponible','Disponible'),('reservado','Reservado'),('renta','Renta'),('vendido','Vendido'),('servicio','Servicio')],
                             string="Estado",default='almacen',copy=False)
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user, index=True)

    marca = fields.Char(string="Marca")
    rent_price = fields.Float(string="Precio de Renta por Día")
    modelo = fields.Many2one('tools.modelo',string="Modelo")
    categoria = fields.Many2one('tools.categoria', string="Categoria")
    date_compra = fields.Date(string="Año de Compra")
    date_fabric = fields.Date(string="Año de Fabricacion")
    descripcion = fields.Char(string="Descripcion")
    tipo = fields.Selection([('aditamento', 'Aditamento'), ('accesorio', 'Accesorio')],
                            string="Tipo", copy=False, required=True)
    car = fields.Many2one('fleet.vehicle', string="Vehículo Asociado")
    tiempo_de_depreciacion = fields.Integer(string="Duración de Depreciación Contable", required=True)
    periodo_de_depreciacion = fields.Selection([('1', 'Meses'), ('12', 'Años')], string='Periodo de Depreciación',
                                               default='1')
    depreciacion_contable = fields.Many2one('account.asset', string="Depreciación Contable",
                                            context="{'form_view_ref':'account_asset.view_account_asset_form'}")
    depreciacion_fiscal = fields.Many2one('account.asset', string="Depreciación Fiscal",
                                          context="{'form_view_ref':'account_asset.view_account_asset_form'}")
    residual_value = fields.Monetary(related='depreciacion_contable.book_value',string="Valor residual")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')



    def unlink(self):
        if self.id == True:
            raise UserError('No se puede eliminar ningun Accesorio o Aditamento registrado!')
        return super(CarTools, self).unlink()


    def vendido(self):
        self.state = 'vendido'

    def depreciacion(self):
        vals = self.env['ir.sequence'].next_by_code('secuencia.aditamentos')
        self.state = 'disponible'
        self.ensure_one()
        if self.tipo == 'aditamento':
            activo = self.env['account.asset']
            valores_activo = {}
            valores_activo.update({
                'name': '%s %s Fiscal' % (self.name,self.categoria.name),
                'original_value': self.costo,
                'acquisition_date': date.today(),
                'method': 'linear',
                'method_period': '1',
                'first_depreciation_date': date.today(),
                'account_asset_id': self.categoria.activo.id,
                'account_depreciation_id': self.categoria.amortizacion.id,
                'account_depreciation_expense_id': self.categoria.gasto.id,
                'journal_id': self.categoria.diario.id,
                'state': 'draft',
                'asset_type': 'purchase',
                'method_number': 48,
                'aditamento': self.id,
            })
            activo_creado = activo.create(valores_activo)
            self.depreciacion_fiscal = activo_creado.id
            valores_contable={}
            valores_contable.update({
                'name': '%s %s Contable' %(self.name,self.modelo.name),
                'original_value': self.costo,
                'acquisition_date': date.today(),
                'method': 'linear',
                'method_period': self.periodo_de_depreciacion,
                'first_depreciation_date': date.today(),
                'account_asset_id': self.modelo.activo.id,
                'account_depreciation_id': self.modelo.amortizacion.id,
                'account_depreciation_expense_id': self.modelo.gasto.id,
                'journal_id': self.modelo.diario.id,
                'state': 'draft',
                'salvage_value': self.costo * .15,
                'asset_type': 'purchase',
                'method_number': self.tiempo_de_depreciacion,
                'aditamento': self.id,
            })
            contable_creado = activo.create(valores_contable)
            self.depreciacion_contable = contable_creado.id
            self.num_eco = vals
        else:
            self.num_eco = vals


    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']

    def actividades(self):
        accesorios = self.env['car.tools'].search([])
        for accesorio in accesorios:
            if not accesorio.car.id:
                accesorio.activity_schedule('ligar_vehiculo_tools',user_id=accesorio.env['res.users'].id)
            else:
                return True








