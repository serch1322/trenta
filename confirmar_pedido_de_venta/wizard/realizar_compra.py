# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class realizarCompra(models.TransientModel):
    _name = "de.compras"

    @api.depends('order_line.subtotal')
    def _obtener_totales(self):
        total_concepts = 0.0
        for compra in self:
            for line in compra.order_line:
                total_concepts = total_concepts + line.subtotal
            compra.total_concepts = total_concepts

    @api.onchange('order')
    def _llenar_lista(self):
        for record in self:
            record.write({'order_line':[(5,0,0)]})
            venta = self.env['sale.order'].search([('name', '=', record.order.name)])
            lista_a_comprar = {}
            lista_comprar = []
            for ventas in venta.order_line:
                if ventas.restante != 0:
                   valores = {
                       'product_id': ventas.product_id,
                       'name': ventas.name,
                       'product_uom_qty': ventas.restante,
                       'price_unit': ventas.price_unit,
                   }
                   lista_comprar.append((0,0,valores))
            lista_a_comprar.update({'order_line': lista_comprar})
        lista_comprada = record.update(lista_a_comprar)

    @api.onchange('name')
    def jalar_orden(self):
        venta = self._context
        orden = self.env['sale.order'].browse(venta['active_id'])
        nombre_orden = {
            'order': orden.id,
        }
        locomprado_creado = self.write(nombre_orden)


    name = fields.Many2one('res.partner',string="Proveedor", required=True)
    order = fields.Many2one('sale.order',string="Orden de Venta", compute="jalar_orden")
    order_line = fields.One2many('de.compras.line', 'order_id', string='Order Lines', copy=True, auto_join=True)
    total_concepts = fields.Float(string="Total", compute="_obtener_totales", store=True)


    def generar_orden_compra(self):
        self.ensure_one()
        #mandar a modulo de compras
        a_compra = self.env['purchase.order']
        vamonos_de_compras = {}
        vamonos_de_compras.update({
            'partner_id': self.name.id,
            'venta_origen': self.order.id,
        })
        lista_compras = []
        if self.order_line:
            for linea in self.order_line:
                if linea.product_id:
                    lineas_compra = {
                        'product_id': linea.product_id.id,
                        'product_qty': linea.qty_comprada,
                        'price_unit': linea.product_id.standard_price,
                    }
                    lista_compras.append((0, 0, lineas_compra))
        if lista_compras:
            vamonos_de_compras.update({
                'order_line': lista_compras,
            })
        lista_creada = a_compra.create(vamonos_de_compras)

        # Regresar lo comprado a modulo de ventas
        venta = self._context
        orden = self.env['sale.order'].browse(venta['active_id'])
        for linea in self.order_line:
                for compra in orden.order_line:
                    if linea.product_id.id == compra.product_id.id:
                        lineas_compradas = {
                            'comprados': linea.qty_comprada,
                        }
                        locomprado_creado = compra.write(lineas_compradas)

class realizarCompleLineas(models.TransientModel):
    _name = "de.compras.line"

    @api.depends('qty_comprada', 'price_unit')
    def _get_subtotal(self):
        for line in self:
            line.subtotal = line.qty_comprada * line.price_unit

    @api.onchange('qty_comprada')
    def limitar_comprados(self):
        for line in self:
            if line.qty_comprada > line.product_uom_qty:
                raise ValidationError(_('No se puede comprar mas de lo vendido'))

    order_id = fields.Many2one('de.compras', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Producto')
    name = fields.Text(string='Descripcion', required=True)
    product_uom_qty = fields.Float(string='Faltante', digits='Product Unit of Measure', readonly=True, required=True, default=0.0)
    qty_comprada = fields.Float('Comprado', copy=False, store=True, digits='Product Unit of Measure', default=0.0, required=True)
    price_unit = fields.Float('Precio Unitario', required=True, digits='Product Price', default=0.0)
    subtotal = fields.Float(string="Subtotal", compute="_get_subtotal", store=True)


