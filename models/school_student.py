from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
import random
import time


class SchoolStudent(models.Model):
    _name = 'school.student'
    # _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student'

    # partner_id = fields.Many2one(
    #         'res.partner', string='Partner', required=True, ondelete='cascade', index=True, auto_join='res.partner'
    # )
    student_number = fields.Char(string='Student Number', required=True, copy=False, readonly=True, default=_('New'))
    id_number = fields.Char(string='ID Number', copy=False, unique=True, required=True)

    name = fields.Char(string='Student Name', required=True, tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', required=True)
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    # حقل الجنسية
    nationality_id = fields.Many2one('res.nationality', string='Nationality', required=True)
    address = fields.Char(string='Address', tracking=True)

    # حقل المحافظة (الولاية)
    # state_id = fields.Many2one('res.country.state', string="State", required=True)

    # حقل الدولة مرتبط بالمحافظة
    #     country_id = fields.Many2one('res.country', string="Country", related='state_id.country_id', store=True)

    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today, required=True)
    guardian_name = fields.Char(string="Guardian Name")
    guardian_relationship = fields.Selection(
            [
                    ('father', 'Father'),
                    ('mother', 'Mother'),
                    ('guardian', 'Guardian'),
            ], string="Guardian Relationship", tracking=True)
    guardian_phone = fields.Char(string="Guardian Phone Number")
    education_stage = fields.Selection(
            [('1', 'Grade 1'), ('2', 'Grade 2'),
             ('3', 'Grade 3'), ('4', 'Grade 4'),
             ('5', 'Grade 5'), ('6', 'Grade 6'), ],
            string='Education Stage', required=True, default='1', tracking=True)

    color = fields.Integer(string='Color', default=lambda self: random.randint(0, 11))

    total_absences = fields.Integer(string='Total Absences')
    health_status = fields.Text(string="Health Status")
    allergies = fields.Text(string="Allergies")
    emergency_medical_conditions = fields.Text(string="Emergency Medical Conditions")
    student_photo = fields.Binary(string='Student Photo')
    official_documents = fields.Binary(string='Official Documents')
    achievements = fields.Text(string='Achievements')
    active = fields.Boolean(string="Active", default=True)

    classroom_id = fields.Many2one(
            'school.classroom',
            string='Classroom',
            domain="[('education_stage', '=', education_stage)]",  # إضافة Domain لعرض الفصول وفقاً للمرحلة التعليمية
            tracking=True
    )  # إضافة العلاقة مع الفصول

    classroom_stage = fields.Selection(
            [('1', 'One'), ('2', 'Two')],
            related='classroom_id.classroom_stage',
            string='Classroom Stage', tracking=True)

    # عند استخدام store=True، تصبح القيمة المحسوبة ثابتة ولا تُعاد حسابها تلقائيًا
    # مع كل تغيير في القيم الأخرى، إلا إذا تم تعديل الحقول التي تعتمد عليها دالة compute.
    # عشان كدا خليت تخزين false عشان لو غيرت ماده مثلا من محله الا مرحله او الي فصل تتحدث تلقائي
    subject_ids = fields.Many2many(
            'school.subject', string='Subjects',
            compute='_compute_subjects',
            # ممكن استخدم الدومين لجلب المواد بناء علي المرحله التعليميه والمرحله الصفية
            # domain="[('education_stage', '=', education_stage), ('classroom_stage', '=', classroom_stage)]",  # عرض المواد وفقاً للمرحلة التعليمية
            store=False  # إزالة التخزين لجعلها ديناميكية

    )

    grade_ids = fields.One2many(
            'student.subject.grade', 'student_id',
            domain="[('education_stage', '=', education_stage),]",  # عرض الدرجات فقط للمرحلة الحالية
            string='Grades', tracking=True)

    historical_ids = fields.One2many('student.stage.history', 'student_id', string='Student History')

    @api.constrains('id_number')
    def _check_unique_id_number(self):
        for record in self:
            # البحث عن أي سجل آخر يحتوي على نفس id_number
            existing_record = self.search([('id_number', '=', record.id_number), ('id', '!=', record.id)])
            if existing_record:
                raise ValidationError('The ID Number must be unique!')

    # دا بيحسب وبيجيب المواد بناء علي المواد اللي موجوده في الفصل الدراسي
    @api.depends('education_stage', 'classroom_stage', )
    def _compute_subjects(self):
        for student in self:
            if student.education_stage and student.classroom_stage:
                # الحصول على المواد المرتبطة بالفصل الدراسي مع المرحلة التعليمية والصفية
                subjects = self.env['school.subject'].search(
                        [
                                ('education_stage', '=', student.education_stage),
                                ('classroom_stage', '=', student.classroom_stage),
                        ])
                student.subject_ids = subjects
                #     or
                # student.subject_ids = [(6, 0, subjects.ids)]  # تعيين المواد للطالب
            else:
                student.subject_ids = False  # إذا لم يكن هناك فصل، اجعل الحقل فارغًا
                # or
                # student.subject_ids = [(5, 0, 0)]  # إذا لم يكن هناك فصل، اجعل الحقل فارغًا

    @api.constrains('grade_ids')  # تحديد قيود التحقق عند تعديل أو إضافة حقل grade_ids
    def _check_unique_subjects(self):
        for student in self:  # تكرار على كل سجل (طالب) في self
            # نحصل على جميع المواد المرتبطة بهذا الطالب عن طريق الوصول إلى حقل grade_ids الذي يحتوي على درجات المواد
            subject_ids = [grade.subject_id.id for grade in student.grade_ids if grade.subject_id]

            # التحقق من وجود تكرار في المواد
            # إذا كان طول قائمة subject_ids لا يساوي طول المجموعة set(subject_ids)
            # فهذا يعني أن هناك تكرارًا في المواد (لأن set تقوم بإزالة العناصر المكررة)
            if len(subject_ids) != len(set(subject_ids)):
                # إذا وجدنا تكرارًا، نقوم برفع خطأ ValidationError ليمنع المستخدم من الحفظ
                raise ValidationError(_(f'You cannot assign the same subject more than once for the same student {student.name}.'))

    @api.model
    def write(self, vals):
        # التحقق من الأذونات
        # if not self.env.user.has_group('your_module.group_name'):
        #     raise UserError('ليس لديك الأذونات اللازمة لتغيير المرحلة التعليمية للطالب.')

        # اذا تم تغيير قيمة الحقل education_stage
        if 'education_stage' in vals:
            # الحصول على المرحلة التعليمية الجديدة من القيم المرسلة
            new_stage = vals.get('education_stage')
            print(f"New Stage: {new_stage}")

            # جلب المرحلة التعليمية القديمة وحفظها مع الدرجات في السجل
            old_stage = self.education_stage if self.education_stage else False
            print(f"Old Stage: {old_stage}")
            if old_stage:
                old_stage_label = dict(self._fields['education_stage'].selection).get(old_stage, _('Unknown'))

                for student in self:
                    # جلب جميع المواد المرتبطة بالمرحلة التعليمية القديمة (الحالية)
                    old_subjects = self.env['school.subject'].search(
                            [('education_stage', '=', student.education_stage)]
                    )
                    # استخدام mapped للحصول على معرفات المواد
                    # old_subject_ids = old_subjects.mapped('id')

                    print(f"Old Subjects: {old_subjects}")

                    # التحقق إذا كانت المرحلة التعليمية القديمة ليس لها مواد
                    # if not old_subjects:
                    #     raise UserError(
                    #             'المرحلة التعليمية الحالية ليس لها مواد، لا يمكن الانتقال إلى المرحلة التعليمية التالية.\n'
                    #             'يرجى تعيين مواد لها من النموذج الخاص بالمواد.'
                    #     )

                    # جلب جميع المواد المرتبطة بالمرحلة التعليمية الجديدة
                    new_subjects = self.env['school.subject'].search(
                            [('education_stage', '=', new_stage)]
                    )
                    print(f"New Subjects: {new_subjects}")

                    # جلب جميع درجات الطالب الحالية المتعلقة بالمرحلة الحالية فقط
                    student_grades = self.env['student.subject.grade'].search(
                            [('student_id', '=', student.id),
                             # ('subject_id', 'in', old_subject_ids),
                             # or
                             ('subject_id', 'in', old_subjects.ids), ]  # الدرجات المتعلقة بالمواد الخاصة بالمرحلة الحالية
                    )
                    print(f"Student Grades: {student_grades}")

                    # التأكد من أن جميع المواد الخاصة بالمرحلة القديمة قد تم إدخال درجاتها
                    if len(old_subjects) > len(student_grades):
                        raise UserError('يجب إدخال جميع الدرجات للمواد المرتبطة بالمرحلة التعليمية الحالية قبل الانتقال الى المرحلة التعليمية التالية.')

                    # قائمة لتخزين المواد التي فشل فيها الطالب
                    failed_subjects = []
                    for grade in student_grades:
                        if grade.grade < grade.max_grade * 0.5:
                            failed_subjects.append(grade.subject_id.name)  # إضافة اسم المادة التي فشل فيها الطالب

                    # إذا كانت هناك مواد فشل فيها الطالب، نمنع الانتقال للمرحلة الجديدة
                    if failed_subjects:
                        raise UserError(f'الطالب {student.name} فشل في المواد التالية: {", ".join(failed_subjects)} ولا يمكنه الانتقال إلى المرحلة التعليمية التالية.')
                        # البحث عن الدرجات القديمة
                        # إخفاء الدرجات القديمة
                    # حفظ الدرجات المتعلقة بالمرحلة القديمة
                    self.env['student.stage.history'].create(
                            {
                                    'student_id'     : student.id,
                                    'old_stage'      : old_stage_label,
                                    'education_stage': new_stage,
                                    'date'           : fields.Datetime.now(),
                                    'grade_ids'      : [(6, 0, student_grades.ids)],  # حفظ درجات المرحلة الحالية
                                    'old_subject_ids': [(6, 0, old_subjects.ids)],  # حفظ المواد الخاصة بالمرحلة القديمة
                                    # 'new_subject_ids': [(6, 0, new_subjects.ids)],  # يمكن حفظ المواد الخاصة بالمرحلة الجديدة عند الحاجة
                            })

        # تنفيذ عملية الكتابة الأصلية بعد التحقق
        res = super(SchoolStudent, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        # تحقق من عدم وجود أرقام طلاب مكررة قبل الإنشاء
        existing_student = self.search([('id_number', '=', vals.get('id_number'))], limit=1)
        if existing_student:
            raise ValidationError("رقم الهوية موجود بالفعل!")

        if vals.get('student_number', _('New')) == _('New'):
            vals['student_number'] = self.env['ir.sequence'].next_by_code('student_seq') or _('New')

        # تحقق من المواد الدراسية المكررة قبل الإنشاء
        student = super(SchoolStudent, self).create(vals)
        student._check_unique_subjects()

        # إضافة سجل جديد إلى تاريخ المراحل
        self.env['student.stage.history'].create(
                {
                        'student_id'     : student.id,
                        'education_stage': student.education_stage,
                        'old_stage'      : False,  # لا يوجد مرحلة قديمة عند الإنشاء
                        'date'           : fields.Date.today(),
                        'enrollment_date': student.enrollment_date,
                }
        )

        return student

    # لو عايز رقم الهاتف ارقام فقط
    # @api.constrains('phone', 'guardian_phone')
    # def _check_phone_numbers(self):
    #     for record in self:
    #         if record.phone and not record.phone.isdigit():
    #             raise ValidationError("رقم الهاتف يجب أن يحتوي على أرقام فقط.")
    #         if record.guardian_phone and not record.guardian_phone.isdigit():
    #             raise ValidationError("رقم هاتف الوصي يجب أن يحتوي على أرقام فقط.")

    @api.constrains('phone', 'guardian_phone')
    def _check_phone_number(self):
        # phone_pattern = re.compile(r'^\d{10,15}$')  # يسمح فقط بالأرقام من 10 إلى 15 بدون رمز "+"
        # phone_pattern = re.compile(r'^\d{10}$')  # فرض أن الرقم يجب أن يكون بالضبط 10 أرقام

        phone_pattern = re.compile(r'^\+?\d{10,15}$')  # يسمح بالأرقام من 10 إلى 15 مع رمز الدولة (+) اختياري
        for record in self:
            if record.phone:
                # تحقق إذا كان الرقم يتوافق مع النمط
                if not phone_pattern.match(record.phone):
                    raise ValidationError(_("Phone number must be between 10 and 15 digits and can start with '+'."))

            if record.guardian_phone:
                if not phone_pattern.match(record.guardian_phone):
                    raise ValidationError(_("Guardian phone must be between 10 and 15 digits and can start with '+'."))

    @api.constrains('email')
    def _check_email(self):
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')  # نمط للتحقق من صيغة البريد الإلكتروني
        for record in self:
            if record.email:
                # تحقق من صحة البريد الإلكتروني
                if not email_pattern.match(record.email):
                    raise ValidationError("Invalid email format. Please enter a valid email address.")

    def level_stage_one(self):
        for record in self:
            self.education_stage = '1'
            self.classroom_id = False

    def level_stage_two(self):
        for record in self:
            self.education_stage = '2'
            self.classroom_id = False

    def level_stage_three(self):
        for record in self:
            self.education_stage = '3'
            self.classroom_id = False

    def level_stage_four(self):
        for record in self:
            self.education_stage = '4'
            self.classroom_id = False

    def level_stage_five(self):
        for record in self:
            self.education_stage = '5'
            self.classroom_id = False

    def level_stage_six(self):
        for record in self:
            self.education_stage = '6'
            self.classroom_id = False
