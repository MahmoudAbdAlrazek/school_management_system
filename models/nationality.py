from odoo import models, fields, api


class Nationality(models.Model):
    _name = 'res.nationality'
    _description = 'Nationality'

    name = fields.Char(string='Nationality', required=True)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            # تحويل أول حرف من كل كلمه إلى كابتل
            self.name = self.name.title()
