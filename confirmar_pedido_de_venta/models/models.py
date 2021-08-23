# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EstadoConfirmarPedido(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.restante')
    def get_total_restante(self):
        total_concepts = 0.0
        for order in self:
            for line in order.order_line:
                total_concepts = total_concepts + line.restante
            order.total_restante = total_concepts

    compras_count = fields.Integer(compute="count_all", string="Compras Generadas")
    total_restante = fields.Float(compute="get_total_restante", default=0.0)
    total_comprado = fields.Float(compute="get_total_comprado",default=0.0)
    margen_ganancia = fields.Float(compute="get_total_comprado")
    porcentaje_ganancia = fields.Float(compute="get_total_comprado")

    def get_total_comprado(self):
        compras = self.env['purchase.order'].search([('venta_origen', '=', self.name)])
        for record in self:
            if record.compras_count != 0:
                for compra in compras:
                    record.total_comprado = record.total_comprado + compra.amount_untaxed
                    record.margen_ganancia = record.amount_untaxed - record.total_comprado
                    record.porcentaje_ganancia = record.margen_ganancia / record.amount_untaxed
            else:
                record.total_comprado = 0.0
                record.margen_ganancia = 0.0
                record.porcentaje_ganancia = 0.0

    def return_actions_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('purchase.%s' % xml_id)
            res.update(
                #context=dict(self.env.context, default_order_id=self.id, group_by=False),
                domain=[('venta_origen', '=', self.name)]
            )
            return res
        return False

    def count_all(self):
        compras = self.env['purchase.order']
        for record in self:
            record.compras_count = compras.search_count([('venta_origen', '=', record.name)])

class EstadoConfirmarPedido(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('comprado','product_uom_qty')
    def sacar_restante(self):
        for record in self:
            record.restante = record.product_uom_qty - record.comprado

    comprado = fields.Float(compute="cuenta_comprado",string="Comprado", store=True, default=0.0)
    comprados = fields.Float(string="Comprados", store=True, default=0.0)
    restante = fields.Float(compute="sacar_restante",string="Faltante", store=True, default=0.0)

    @api.depends('comprados')
    def cuenta_comprado(self):
        for record in self:
            record.comprado = record.comprados + record.comprado



class ModificarCompra(models.Model):
    _inherit = 'purchase.order'

    origin = fields.Char('Source Document', copy=False,
                         help="Reference of the document that generated this purchase order "
                              "request (e.g. a sales order)")
    venta_origen = fields.Many2one('sale.order',help="Pedido de Venta", string="Pedido de Venta Ligado")