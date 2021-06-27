# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class EntidadMatricula(models.Model):
    _inherit = ['fleet.vehicle']

    num_eco = fields.Char(string="Número Económico", copy=False, index=True)
    entidad = fields.Many2one('res.country.state', string="Entidad de Matricula")
    serie_motor = fields.Char(string="Numero de Serie Motor")
    numero_cilindros = fields.Float(string="Numero de Cilindros")
    seats = fields.Integer(string="Numero de Pasajeros", help='Number of seats of the vehicle')
    carga= fields.Float(string="Capacidad de Carga")
    categoria = fields.Many2one('car.category',string="Categoria de Vehiculo")
    tipo = fields.Selection(related='categoria.tipo')
    depr = fields.Selection([('total', 'Depreciación Total (100%)'), ('parcial', 'Depreciación Parcial ($175,000)')],string="Tipo de Depreciación Fiscal",default=False)
    inventario = fields.Many2one('account.account',string="Cuenta de Inventario")
    insurance_count = fields.Integer(compute="_compute_count_all", string="Seguro", store=True)
    tools_count = fields.Integer(compute="_compute_count_all", string="Accesorios/Aditamentos", store=True)
    facturas_count = fields.Integer(compute="_compute_count_all", string="Facturas", store=True)
    tiempo_de_depreciacion = fields.Integer(string="Duración de Depreciación Contable",required=True)
    periodo_de_depreciacion = fields.Selection([('1', 'Meses'), ('12', 'Años')], string='Periodo de Depreciación', default='1')
    depreciacion_contable =  fields.Many2one('account.asset',string="Depreciación Contable")
    depreciacion_fiscal = fields.Many2one('account.asset', string="Depreciación Fiscal")
    car_value = fields.Float(string="Valor de la Compra (IVA incluido)")
    depreciado = fields.Boolean(string="¿Depreciado?",default=False,copy=False)
    fuel_type = fields.Selection([('gasoline', 'Gasoline'),
                                  ('diesel', 'Diesel'),
                                  ('electric', 'Electric'),
                                  ('hybrid', 'Hybrid'),
                                  ('petrol', 'Petrol')],
                                 'Fuel Type', help='Fuel Used by the vehicle')
    color = fields.Char(string='Color', default='#FFFFFF')
    _sql_constraints = [('vin_sn_unique', 'unique (vin_sn)', "Chassis Number already exists !"),
                        ('license_plate_unique', 'unique (license_plate)', "License plate already exists !")]

    def return_actions_to_open_seguro(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('fleet_rental.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('state', '=', 'corriendo'), ('lineas_ids.car', '=', self.id)]
            )
            return res
        return False

    def return_actions_to_open_factura(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('invoice_line_ids.vehiculo', '=', self.id),('state','=','posted'),('move_type','=','out_invoice')]
            )
            return res
        return False

    def return_actions_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('fleet_rental.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('car', '=', self.id)]
            )
            return res
        return False

    def return_actions_to_open_venta_vehiculo(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        venta = self.env['venta.vehiculo']
        venta_creada = {}
        venta_creada.update({
            'name': self.model_id.id,
            'numero_bastidor': self.vin_sn,
        })
        activo_creado = venta.create(venta_creada)
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('fleet_rental.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('name', '=', self.model_id.id)]
            )
            return res
        return False

    def _compute_count_all(self):
        Odometer = self.env['fleet.vehicle.odometer']
        LogService = self.env['fleet.vehicle.log.services']
        LogContract = self.env['fleet.vehicle.log.contract']
        insurance = self.env['car.insurance']
        tools = self.env['car.tools']
        facturas = self.env['account.move.line']
        for record in self:
            record.odometer_count = Odometer.search_count([('vehicle_id', '=', record.id)])
            record.service_count = LogService.search_count([('vehicle_id', '=', record.id)])
            record.contract_count = LogContract.search_count(
                [('vehicle_id', '=', record.id), ('state', '!=', 'closed')])
            record.history_count = self.env['fleet.vehicle.assignation.log'].search_count(
                [('vehicle_id', '=', record.id)])
            record.insurance_count = insurance.search_count(
                [('lineas_ids.car', '=', record.id), ('state', '=', 'corriendo')])
            record.tools_count = tools.search_count([('car', '=', record.id)])
            record.facturas_count = facturas.search_count([('vehiculo', '=', record.id),('move_id.state','=','posted'),('move_id.move_type','=','out_invoice')])

    def depreciacion(self):
        vals = self.env['ir.sequence'].next_by_code('secuencia.vehiculos')
        state_id = self.env.ref('fleet_rental.vehicle_state_active').id
        self.write({'state_id': state_id})
        self.ensure_one()
        activo = self.env['account.asset'].ref("account_asset.view_account_asset_form")
        valores_activo = {}
        if self.tipo == 'carga':
            valores_activo.update({
                'name': '%s %s %s Fiscal' % (self.model_id.name,self.model_id.brand_id.name,self.license_plate),
                'original_value': self.net_car_value,
                'acquisition_date': date.today(),
                'method': 'linear',
                'method_period': '1',
                'first_depreciation_date': date.today(),
                'account_asset_id': self.categoria.activo.id,
                'account_depreciation_id': self.categoria.amortizacion.id,
                'account_depreciation_expense_id': self.categoria.gasto.id,
                'journal_id': self.categoria.diario.id,
                'state': 'open',
                'asset_type': 'purchase',
                'method_number': 48,
                'vehiculo': self.id,
        })
        elif self.depr == 'total':
            valores_activo.update({
                'name': '%s %s %s Fiscal' % (self.model_id.name, self.model_id.brand_id.name, self.license_plate),
                'original_value': self.net_car_value,
                'acquisition_date': date.today(),
                'method': 'linear',
                'method_period': '1',
                'first_depreciation_date': date.today(),
                'account_asset_id': self.categoria.activo.id,
                'account_depreciation_id': self.categoria.amortizacion.id,
                'account_depreciation_expense_id': self.categoria.gasto.id,
                'journal_id': self.categoria.diario.id,
                'state': 'open',
                'asset_type': 'purchase',
                'method_number': 1,
                'vehiculo': self.id,
            })
        elif self.depr == 'parcial' and self.net_car_value > 175000:
            valores_activo.update({
                'name': '%s %s %s Fiscal' % (self.model_id.name, self.model_id.brand_id.name, self.license_plate),
                'original_value': self.net_car_value,
                'acquisition_date': date.today(),
                'method': 'linear',
                'method_period': '1',
                'first_depreciation_date': date.today(),
                'account_asset_id': self.categoria.activo.id,
                'account_depreciation_id': self.categoria.amortizacion.id,
                'account_depreciation_expense_id': self.categoria.gasto.id,
                'journal_id': self.categoria.diario.id,
                'state': 'open',
                'asset_type': 'purchase',
                'method_number': 48,
                'salvage_value': self.net_car_value - 175000,
                'vehiculo': self.id,
            })
        else:
            valores_activo.update({
                'name': '%s %s %s Fiscal' % (self.model_id.name, self.model_id.brand_id.name, self.license_plate),
                'original_value': self.net_car_value,
                'acquisition_date': date.today(),
                'method': 'linear',
                'method_period': '1',
                'first_depreciation_date': date.today(),
                'account_asset_id': self.categoria.activo.id,
                'account_depreciation_id': self.categoria.amortizacion.id,
                'account_depreciation_expense_id': self.categoria.gasto.id,
                'journal_id': self.categoria.diario.id,
                'state': 'open',
                'asset_type': 'purchase',
                'method_number': 48,
                'vehiculo': self.id,
            })
        activo_creado = activo.create(valores_activo)
        self.depreciacion_fiscal = activo_creado.id
        valores_contable={}
        valores_contable.update({
            'name': '%s %s %s Contable' % (self.model_id.name, self.model_id.brand_id.name, self.license_plate),
            'original_value': self.net_car_value,
            'acquisition_date': date.today(),
            'method': 'linear',
            'method_period': self.periodo_de_depreciacion,
            'first_depreciation_date': date.today(),
            'account_asset_id': self.model_id.activo.id,
            'account_depreciation_id': self.model_id.amortizacion.id,
            'account_depreciation_expense_id': self.model_id.gasto.id,
            'journal_id': self.model_id.diario.id,
            'state': 'open',
            'salvage_value': self.net_car_value * .15,
            'asset_type': 'purchase',
            'method_number': self.tiempo_de_depreciacion,
            'vehiculo': self.id,
        })
        contable_creado = activo.create(valores_contable)
        self.depreciacion_contable = contable_creado.id
        self.depreciado = True
        self.num_eco = vals



class DepreciacionModelos(models.Model):
    _inherit = ['fleet.vehicle.model']

    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)
    diario = fields.Many2one('account.journal', string="Diario", required=True, domain="[('type', '=', 'general')]")

class ventaVehiculo(models.Model):
    _name = 'venta.vehiculo'
    _description = 'Venta'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    venta = fields.Selection([('sin', 'Sin Accesorios/Aditamentos'), ('con', 'Con Accesorios/Aditamentos')], string="Tipo de Venta", copy=False)
    name = fields.Many2one('fleet.vehicle',string="Vehículo", required=True, domain="[('insurance_count','=','0')]")
    numero_bastidor = fields.Char(string="Numero de Serie de Vehículo", required=True)


    def vender(self, cr, uid, ids, context=None):
        tools = self.env['car.tools'].search([])
        if self.venta == 'sin':
            for tool in tools:
                if tool.car == self.name.id:
                    tl_ids = tool.search(cr, uid, [('car', '=', self.name.id)], context=context)
                    tools.unlink(cr, uid, tl_ids, context=context)




