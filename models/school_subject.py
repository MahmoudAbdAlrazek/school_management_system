from odoo import models, fields, api
import random


class SchoolSubject(models.Model):
    _name = 'school.subject'  # اسم الموديل
    _description = 'School Subject'

    name = fields.Char(string='Subject Name', required=True)  # اسم المادة
    code = fields.Char(string='Subject Code', required=True)  # رمز المادة
    description = fields.Text(string='Description')  # وصف المادة
    credit_hours = fields.Integer(string='Credit Hours', default=3)  # عدد الساعات المعتمدة

    classroom_id = fields.Many2one(
            'school.classroom',
            string='Classroom',
    )

    teacher_ids = fields.Many2many('school.teacher', string='Teachers')  # المدرسين المسؤولين عن تدريس المادة

    color = fields.Integer(string='Color', default=lambda self: random.randint(0, 11))

    max_grade = fields.Float(string='Maximum Grade', required=True, )

    student_ids = fields.Many2many('school.student', string='Student Name', )

    subject_grade_ids = fields.One2many(
            'student.subject.grade',
            'subject_id',
            string='Subject Grades',
    )

    # حقل جديد لتحديد المرحلة التعليمية التي تتبع لها المادة
    education_stage = fields.Selection(
            [
                    ('1', 'Grade 1'),
                    ('2', 'Grade 2'),
                    ('3', 'Grade 3'),
                    ('4', 'Grade 4'),
                    ('5', 'Grade 5'),
                    ('6', 'Grade 6'),
            ],
            string='Education Stage',  # المرحلة التعليمية
            required=True,
            # default='1',  # تعيين القيمة الافتراضية للمرحلة الأولى
    )
    classroom_stage = fields.Selection(
            [('1', 'Classroom 1'), ('2', 'Classroom 2')],
            string='Classroom Stage',
            required=True,
    )

    def write(self, vals):
        # حفظ القيم الحالية
        result = super(SchoolSubject, self).write(vals)

        # إذا تم تغيير المرحلة التعليمية أو الصفية
        if 'education_stage' in vals or 'classroom_stage' in vals:
            # البحث عن الطلاب المتأثرين
            affected_students = self.env['school.student'].search(
                    [
                            ('subject_ids', 'in', self.ids)
                    ])
            for student in affected_students:
                student._compute_subjects()  # إعادة حساب المواد للطلاب المتأثرين

        return result

    @api.model
    def create(self, vals):
        # إنشاء المادة الجديدة
        subject = super(SchoolSubject, self).create(vals)

        # البحث عن الطلاب المتأثرين
        affected_students = self.env['school.student'].search(
                [
                        ('subject_ids', 'in', [subject.id])
                ])
        for student in affected_students:
            student._compute_subjects()  # إعادة حساب المواد للطلاب المتأثرين

        return subject
