# -*- coding: utf-8 -*-
# from odoo import http


# class ConfirmarPedidoDeVenta(http.Controller):
#     @http.route('/confirmar_pedido_de_venta/confirmar_pedido_de_venta/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/confirmar_pedido_de_venta/confirmar_pedido_de_venta/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('confirmar_pedido_de_venta.listing', {
#             'root': '/confirmar_pedido_de_venta/confirmar_pedido_de_venta',
#             'objects': http.request.env['confirmar_pedido_de_venta.confirmar_pedido_de_venta'].search([]),
#         })

#     @http.route('/confirmar_pedido_de_venta/confirmar_pedido_de_venta/objects/<model("confirmar_pedido_de_venta.confirmar_pedido_de_venta"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('confirmar_pedido_de_venta.object', {
#             'object': obj
#         })
