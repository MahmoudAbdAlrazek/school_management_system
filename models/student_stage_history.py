from odoo import models, fields, api


class StudentStageHistory(models.Model):
    _name = 'student.stage.history'  # اسم الموديل
    _description = 'Student Stage History'

    student_id = fields.Many2one('school.student', string='Student', ondelete='cascade')  # الطالب
    education_stage = fields.Selection(
            [
                    ('1', 'Grade 1'),
                    ('2', 'Grade 2'),
                    ('3', 'Grade 3'),
                    ('4', 'Grade 4'),
                    ('5', 'Grade 5'),
                    ('6', 'Grade 6'),
            ], string='Education Stage Now', required=True)  # المرحلة
    old_stage = fields.Char(string='Old Stage Education')  # يجب أن يكون من نوع Char
    date = fields.Date(string='Date of Promotion', required=True)  # تاريخ الترقية

    old_subject_ids = fields.Many2many(
            'school.subject',
            'student_old_subject_rel',  # اسم جدول وسيط مخصص للمواد القديمة
            string='Old Subjects')  # المواد القديمة

    new_subject_ids = fields.Many2many(
            'school.subject',
            'student_new_subject_rel',  # اسم جدول وسيط مخصص للمواد الجديدة
            string='New Subjects')  # المواد الجديدة

    enrollment_date = fields.Date(string='Enrollment Date')

    # حقل لحفظ درجات المواد (يمكن أن تكون كما هو موضح سابقًا)

    grade_ids = fields.Many2many('student.subject.grade', string=' Grades')  # استخدام Many2many
