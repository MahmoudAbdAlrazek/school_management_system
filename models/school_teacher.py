from odoo import models, fields, api, _
import random
import re
from odoo.exceptions import ValidationError, UserError


class SchoolTeacher(models.Model):
    _name = 'school.teacher'  # اسم الموديل
    _description = 'School Teacher'

    name = fields.Char(string='Teacher Name', required=True)  # اسم المعلم
    phone = fields.Char(string='Phone Number')  # رقم الهاتف
    email = fields.Char(string='Email')  # البريد الإلكتروني

    subject_ids = fields.Many2many('school.subject', string='Subjects')  # المواد التي يُدرّسها

    classroom_ids = fields.One2many('school.classroom', 'teacher_id', string='Classrooms', readonly=True)  # الفصول التي يُدرّس فيها

    color = fields.Integer(string='Color', default=lambda self: random.randint(0, 11))

    @api.constrains('phone', )
    def _check_phone_number(self):
        # phone_pattern = re.compile(r'^\d{10,15}$')  # يسمح فقط بالأرقام من 10 إلى 15 بدون رمز "+"
        # phone_pattern = re.compile(r'^\d{10}$')  # فرض أن الرقم يجب أن يكون بالضبط 10 أرقام

        phone_pattern = re.compile(r'^\+?\d{10,15}$')  # يسمح بالأرقام من 10 إلى 15 مع رمز الدولة (+) اختياري
        for record in self:
            if record.phone:
                # تحقق إذا كان الرقم يتوافق مع النمط
                if not phone_pattern.match(record.phone):
                    raise ValidationError(_("Phone number must be between 10 and 15 digits and can start with '+'."))

    @api.constrains('email')
    def _check_email(self):
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')  # نمط للتحقق من صيغة البريد الإلكتروني
        for record in self:
            if record.email:
                # تحقق من صحة البريد الإلكتروني
                if not email_pattern.match(record.email):
                    raise ValidationError("Invalid email format. Please enter a valid email address.")
