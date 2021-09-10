# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

class Producto(models.Model):
    _inherit = ['product.template']

    tipo_product = fields.Selection(
        [('aditamento', 'Aditamento'), ('accesorio', 'Accesorio'), ('vehiculo', 'Vehiculo')],
        string="Tipo de Flota", copy=False)
    modelo = fields.Many2one('fleet.vehicle.model', string="Modelo de Vehiculo")
    categoria = fields.Many2one('car.category',string="Categoria de Vehiculo")
    marca = fields.Char(string="Marca")




class registrarRecepcion(models.Model):
    _inherit = ['stock.picking']

    registradoFlota = ('purchase.order')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('registrado', 'Registrado en Flota'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    def registro_flota(self):
        self.ensure_one()
        self.state = 'registrado'
        registro_tools = self.env['car.tools']
        registro_vehiculo = self.env['fleet.vehicle']
        state_id = self.env.ref('fleet_rental.vehicle_state_inventory').id
        aditamento_registro = {}
        accesorio_registro = {}
        vehiculo_registro = {}
        comprado = self._context
        orden = self.env['purchase.order'].browse(comprado['active_id'])
        for linea in self.move_ids_without_package:
            if linea.product_id.tipo_product == 'aditamento':
                for serie in linea.lot_ids:
                    if serie.name:
                        series = serie.name
                        aditamento_registro.update({
                         'name': linea.product_id.name,
                         'costo': linea.product_id.standard_price,
                         'descripcion': linea.product_id.description_sale,
                         'tipo': linea.product_id.tipo_product,
                         'num_serie': series,
                        })
                        aditamento_creado = registro_tools.create(aditamento_registro)
            elif linea.product_id.tipo_product == 'accesorio':
                i = 0
                while i < linea.quantity_done:
                    i += 1
                    accesorio_registro.update({
                        'name': linea.product_id.name,
                        'costo': linea.product_id.standard_price,
                        'descripcion': linea.product_id.description_sale,
                        'tipo': linea.product_id.tipo_product,
                    })
                    accesorio_creado = registro_tools.create(accesorio_registro)
                continue
            elif linea.product_id.tipo_product == 'vehiculo':
                for serie in linea.lot_ids:
                    if serie.name:
                        series = serie.name
                        vehiculo_registro.update({
                            'model_id': linea.product_id.modelo.id,
                            'net_car_value': linea.product_id.standard_price,
                            'inventario': linea.product_id.categ_id.property_stock_valuation_account_id.id,
                            'categoria': linea.product_id.categoria.id,
                            'vin_sn' : series,
                            'state_id': state_id,
                        })
                        vehiculo_creado = registro_vehiculo.create(vehiculo_registro)
                        #self.registradoFlota.registrado = True
                        # Regresar lo registrado a modulo de compras
                        for linea in self:
                            for compra in orden:
                                if linea.state == 'registrado':
                                    lineas_compradas = {
                                        'registrado': linea.registradoFlota,
                                    }
                                    locomprado_creado = compra.write(lineas_compradas)

class QuitarrecibirProductos(models.Model):
    _inherit = ['purchase.order']

    registrado = fields.Boolean(string="Regstrado en Flota",default=False,store=True)