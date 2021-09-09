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
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
                in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
                    products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                ', '.join(pickings_without_lots.mapped('name')),
                ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        return True
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


