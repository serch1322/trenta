# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HeredadContacto(models.Model):
    _inherit = 'res.partner'

    tipo_de_licencia = fields.Selection([('motociclista','Motociclista'),('automovilista','Automovilista'),
                                         ('chofer','Chofer'),('federal','Transporte Federal')],
                                        string="Tipo de Licencia")
    conductor = fields.Boolean(string="¿Es Conductor?", default=False, store=True)
    vigencia = fields.Date(string="Vigencia de Licencia")
    sexo = fields.Selection([('masculino', 'Masculino'), ('femenino', 'Femenino')], string="Sexo", copy=False)
    edad = fields.Integer(string="Edad de Conductor")
    tipo_sangre = fields.Selection([('o+', 'O+'), ('o-', 'O-'), ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'),
                                    ('b-', 'B-'), ('ab+', 'AB+'), ('ab-', 'AB-')], string="Tipo de Sangre", copy=False)
    numero_emergencia = fields.Char(string="Numero de Emergencia")
    contacto_emergencia = fields.Char(string="Nombre Contacto de Emergencia")

    curp = fields.Char(string="CURP de Chofer")

    service_count = fields.Integer(compute="_compute_count_all", string='Services')

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('fleet.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vendor_id', '=', self.id)]
            )
            return res
        return False

    def _compute_count_all(self):
        LogService = self.env['fleet.vehicle.log.services']
        for record in self:
            record.service_count = LogService.search_count([('vendor_id', '=', record.id)])

