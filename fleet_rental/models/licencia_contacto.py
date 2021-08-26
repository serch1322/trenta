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

    curp = fields.Char(string="CURP de Chofer")



