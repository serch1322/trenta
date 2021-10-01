# -*-coding: utf-8 -*-

from datetime import date, datetime
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class aprobar_modificacion(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('por_aprobar', 'Por Aprobar'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_confirm(self, act_type_xmlid='', date_deadline=None, summary='Aprobar Venta',note='Precio de Venta Modificado', **act_values): #activity_schelude
        for linea in self.order_line:
            precio = linea.price_unit
            if precio != linea.product_id.lst_price:
                self.state = 'por_aprobar'
                if self.env.context.get('mail_activity_automation_skip'):
                    return False

                if not date_deadline:
                    date_deadline = fields.Date.context_today(self)
                if isinstance(date_deadline, datetime):
                    _logger.warning("Scheduled deadline should be a date (got %s)", date_deadline)
                if act_type_xmlid:
                    activity_type = self.env.ref(act_type_xmlid,
                                                 raise_if_not_found=False) or self._default_activity_type()
                else:
                    activity_type_id = act_values.get('activity_type_id', False)
                    activity_type = activity_type_id and self.env['mail.activity.type'].sudo().browse(activity_type_id)

                model_id = self.env['ir.model']._get(self._name).id
                activities = self.env['mail.activity']
                for record in self:
                    create_vals = {
                        'activity_type_id': activity_type and activity_type.id,
                        'summary': summary,
                        'automated': True,
                        'note': note,
                        'date_deadline': date_deadline,
                        'res_model_id': model_id,
                        'res_id': record.id,
                        'user_id': record.team_id.user_id.id, #esta parte se agrego, equipo de venta, lider de venta.
                    }
                    create_vals.update(act_values)
                    activities |= self.env['mail.activity'].create(create_vals)
                return activities
            else:
                if self._get_forbidden_state_confirm() & set(self.mapped('state')):
                    raise UserError(_(
                        'It is not allowed to confirm an order in the following states: %s'
                    ) % (', '.join(self._get_forbidden_state_confirm())))

                for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
                    order.message_subscribe([order.partner_id.id])
                self.write({
                    'state': 'sale',
                    'date_order': fields.Datetime.now()
                })

                # Context key 'default_name' is sometimes propagated up to here.
                # We don't need it and it creates issues in the creation of linked records.
                context = self._context.copy()
                context.pop('default_name', None)

                self.with_context(context)._action_confirm()
                if self.env.user.has_group('sale.group_auto_done_setting'):
                    self.action_done()
                return True

    def button_approve(self): #action_confirm
        for linea in self.order_line:
            precio = linea.price_unit
            if precio != linea.product_id.lst_price:
                self.state = 'por_aprobar'
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True