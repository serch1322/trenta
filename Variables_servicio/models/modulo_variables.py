# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'bordado','tinta','proceso_especial','precio_proceso_especial')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        precios = self.env['res.config.settings'].search([])
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            if line.bordado:
                Bordado = self.env.ref('Variables_servicio.variable_bordado').precio
                price = price + (line.bordado * Bordado)
            if line.tinta:
                Tinta = self.env.ref('Variables_servicio.variable_tinta').precio
                price = price + (line.tinta * Tinta)
            if line.proceso_especial:
                price = price + (line.proceso_especial * line.precio_proceso_especial)

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    bordado = fields.Float(string='Bordado')
    tinta = fields.Float(string='Tinta')
    proceso_especial = fields.Float(string='Proceso Especial')
    precio_proceso_especial = fields.Float(string='Precio Proceso Especial')


# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     precio_bordado = fields.Float(string='Precio Bordado')
#     precio_tinta = fields.Float(string='Precio Tinta')