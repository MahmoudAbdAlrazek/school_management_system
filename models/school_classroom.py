from odoo import models, fields, api


class Classroom(models.Model):
    _name = 'school.classroom'  # اسم الموديل
    _description = 'Classroom'

    name = fields.Char(string='Classroom Name', required=True)  # اسم الفصل

    # حقل لتحديد المرحلة التعليمية المرتبطة بالفصل
    education_stage = fields.Selection(
            [
                    ('1', 'Grade 1'), ('2', 'Grade 2'),
                    ('3', 'Grade 3'), ('4', 'Grade 4'),
                    ('5', 'Grade 5'), ('6', 'Grade 6'),
            ], string='Education Stage',  # المرحلة التعليمية
            required=True,
            default='1',  # تعيين القيمة الافتراضية للمرحلة الأولى
    )
    classroom_stage = fields.Selection(
            [('1', 'Classroom 1'), ('2', 'Classroom 2')],
            string='Classroom Stage',
            required=True,

    )

    # عند استخدام store=True، تصبح القيمة المحسوبة ثابتة ولا تُعاد حسابها تلقائيًا
    # مع كل تغيير في القيم الأخرى، إلا إذا تم تعديل الحقول التي تعتمد عليها دالة compute.
    # عشان كدا خليت تخزين false عشان لو غيرت ماده مثلا من محله الا مرحله او الي فصل تتحدث تلقائي

    subject_ids = fields.One2many(
            'school.subject',
            'classroom_id',
            string='Subjects',
            compute='_compute_subjects',  # استخدم دالة compute لتحديث المواد
            store=False  # إزالة التخزين لجعلها ديناميكية
    )

    teacher_id = fields.Many2one('school.teacher', string='Teacher', required=True)  # المدرس المسؤول
    teacher_ids = fields.Many2many('school.teacher', string='Teachers of the class')

    student_ids = fields.One2many('school.student', 'classroom_id', string='Students')  # الطلاب الملتحقين بالفصل

    teacher_subjects = fields.Char(string='Teacher Subjects', compute='_get_teacher_subjects')

    # دالة حسابية لتحديد المواد الدراسية بناءً على المرحلة التعليمية ورقم الفصل الدراسي (اول - ثاني )
    @api.depends('education_stage', 'classroom_stage')
    def _compute_subjects(self):
        for record in self:
            if record.education_stage and record.classroom_stage:
                # جلب المواد الدراسية بناءً على المرحلة والفصل
                subjects = self.env['school.subject'].search(
                        [
                                ('education_stage', '=', record.education_stage),
                                ('classroom_stage', '=', record.classroom_stage)
                        ])
                record.subject_ids = subjects
            else:
                # إذا لم يتم اختيار المرحلة أو الفصل، يتم إفراغ الحقل
                record.subject_ids = False

    @api.depends('teacher_id')
    def _get_teacher_subjects(self):
        """ جلب المواد التي يدرسها المدرس المختار """
        for rec in self:
            if rec.teacher_id:
                # جلب المواد التي يدرسها المدرس المختار
                subjects = rec.teacher_id.subject_ids.mapped('name')
                rec.teacher_subjects = ', '.join(subjects)
            else:
                rec.teacher_subjects = 'No subjects assigned'
