from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentSubjectGrade(models.Model):
    _name = 'student.subject.grade'  # اسم الموديل
    _description = 'Student Subject Grades'

    # حقل Many2one الذي يشير إلى نموذج الطالب
    student_id = fields.Many2one('school.student', string='Student', required=True, ondelete='cascade', )

    stage_education_student = fields.Selection(
            [('1', 'Grade 1'), ('2', 'Grade 2'),
             ('3', 'Grade 3'), ('4', 'Grade 4'), ('5', 'Grade 5'),
             ('6', 'Grade 6')], related='student_id.education_stage', string='Education Stage Student')
    classroom_stage_student = fields.Selection(
            [
                    ('1', 'one'), ('2', 'two')
            ], related='student_id.classroom_stage', string='Classroom Stage Student')

    # إذا كانت subject_ids هي حقل Many2many في نموذج الطالب
    subject_ids = fields.Many2many(
            related='student_id.subject_ids',
    )

    # تغيير النطاق لحقل subject_id
    subject_id = fields.Many2one(
            'school.subject', string='Subject', required=True,
            # domain="[('id', 'in', subject_ids), ('id', 'not in', used_subject_ids)]",  # إضافة شرط لاستبعاد المواد المستخدمة
    )

    # حقل محسوب لعرض المواد التي تم استخدامها مسبقًا من قبل الطالب
    used_subject_ids = fields.Many2many(
            'school.subject',
            string='Used Subjects',
            compute='_compute_used_subject_ids',
            store=False  # لأن الحقل محسوب ولا يحتاج للتخزين
    )

    classroom_id = fields.Many2one('school.classroom', string='Classroom', related='student_id.classroom_id', readonly=True)

    # المرحلة التعليمية المرتبطة بالمادة
    # عامل عِلاقة related مع المواد عشان اجيب مرحله الفصل الدراسي من هناك ويكون صحيح

    education_stage = fields.Selection(
            [
                    ('1', 'Grade 1'), ('2', 'Grade 2'),
                    ('3', 'Grade 3'), ('4', 'Grade 4'),
                    ('5', 'Grade 5'), ('6', 'Grade 6'),
            ], string='Education Stage', related='subject_id.education_stage', store=True, readonly=True)

    # المرحلة الصفية المرتبطة بالمادة
    # عامل عِلاقة related مع المواد عشان اجيب مرحله الفصل الدراسي من هناك ويكون صحيح
    classroom_stage = fields.Selection(
            [
                    ('1', 'One'), ('2', 'Two')
            ], string='Classroom Stage', related='subject_id.classroom_stage', readonly=True)

    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    grade = fields.Float(string='Student Grade')  # درجة الطالب
    max_grade = fields.Float(string='Maximum Grade', related='subject_id.max_grade', readonly=True)  # الدرجة النهائية
    is_passed = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Passed Status", compute='_compute_is_passed', store=True)

    history_ids = fields.Many2many(
            'student.stage.history',
            'grade_history_rel',
            'grade_id', 'history_id', string='History Records')  # ربط الدرجات بسجل التاريخ

    # داله  لحساب المواد التي تم استخدامها مسبقًا من قبل الطالب
    active = fields.Boolean(string='Is Archived', default=True, readonly=True)  # حقل للأرشفة

    @api.depends('student_id')  # تحديد أن هذه الدالة تعتمد على تغيير حقل student_id
    def _compute_used_subject_ids(self):
        for record in self:  # التكرار على كل سجل (Record) في self
            if record.student_id:  # إذا كان حقل student_id مُعَيّنًا (ليس فارغًا)
                # البحث عن المواد المستخدمة مسبقًا في السجلات الخاصة بنفس الطالب
                used_subjects = self.env['student.subject.grade'].search(
                        [
                                ('student_id', '=', record.student_id.id)  # البحث عن السجلات المرتبطة بنفس الطالب
                        ]).mapped('subject_id')  # جلب قائمة المواد المرتبطة بهذه السجلات
                # تعيين المواد المستخدمة إلى الحقل used_subject_ids للسجل الحالي
                record.used_subject_ids = used_subjects
                # print(f"Used Subjects for the student: {used_subjects}")  # طباعة قائمة المواد في وحدة التحكم (لأغراض التحقق)
            else:
                # إذا لم يكن هناك طالب معين، قم بتفريغ حقل used_subject_ids
                record.used_subject_ids = []

    @api.depends('grade', 'max_grade')
    def _compute_is_passed(self):
        for record in self:
            if record.max_grade:  # التأكد من أن هناك قيمة للحقل max_grade
                record.is_passed = 'pass' if record.grade >= (record.max_grade * 0.5) else 'fail'
            else:
                record.is_passed = 'fail'  # افتراض أن الطالب راسب إذا لم يكن هناك max_grade

    @api.constrains('grade', 'max_grade')
    def _check_grades(self):
        for record in self:
            if record.grade > record.max_grade:
                raise ValidationError(_("Student grade cannot exceed the maximum grade."))

    # التحقق من عدم وجود سجلات مكررة لنفس الطالب ونفس المادة
    @api.constrains('student_id', 'subject_id')
    def _check_unique_student_subject(self):
        # هذه الدالة تتحقق من عدم وجود سجلات مكررة لنفس الطالب ونفس المادة.
        for record in self:  # نتجول عبر كل سجل من السجلات الحالية
            # البحث عن السجل المكرر بنفس الطالب والمادة مع استبعاد السجل الحالي
            duplicate_record = self.search(
                    [
                            ('student_id', '=', record.student_id.id),  # تحقق من الطالب الحالي
                            ('subject_id', '=', record.subject_id.id),  # تحقق من المادة الحالية
                            ('id', '!=', record.id)  # استبعاد السجل الحالي من البحث
                            #                 عند إضافة أو تعديل سجل، تبحث الدالة عن سجلات أخرى بنفس الطالب والمادة.
                            #         تستخدم شرط ('id', '!=', record.id) لاستبعاد السجل الحالي من البحث.
                            #
                            #     لماذا نستبعد السجل الحالي؟:
                            #         تجنب الأخطاء الزائفة: إذا لم نستبعد السجل الحالي، فسيعتبره النظام سجلًا مكررًا، مما يؤدي إلى رفع خطأ غير ضروري.
                            #         التأكد من وجود سجلات مكررة حقيقية: نستطيع التأكد من أن أي سجل تم العثور عليه هو في الواقع سجل مكرر، وليس السجل الذي نقوم بتعديله.
                            #
                            # النتيجة:
                            #
                            #     إذا وُجد سجل مكرر: يتم رفع خطأ.
                            #     إذا لم يكن هناك سجلات مكررة: يتم السماح بتخزين البيانات الجديدة.
                            #
                            # هذا يضمن أن كل طالب لديه درجة واحدة فقط لكل مادة، دون تكرار غير مرغوب فيه.
                    ],
                    limit=1  # نحصل على السجل المكرر إن وجد، لكن نأخذ سجل واحد فقط
            )
            # print("Duplicate Record:", duplicate_record)
            # إذا وجد سجل مكرر، يتم رفع استثناء لرفض العملية
            if duplicate_record:
                raise ValidationError(
                        _(
                                f"Each student can only have one grade for each subject.\n"
                                f"The subject '{record.subject_id.name}' is already assigned to the student '{record.student_id.name}' "
                                f"with a grade of {duplicate_record.grade}."
                        )
                )

    # التحقق من وجود قيمة سالبة
    @api.constrains('grade')
    def _check_grade(self):
        for record in self:
            if record.grade < 0:
                raise ValidationError(_("Grade cannot be negative."))

    # التحقق لجعل المادة فارغة عند عدم تم تحديد الطالب
    @api.onchange('student_id')
    def _onchange_student_id(self):
        if not self.student_id:
            self.subject_id = False

    # @api.onchange('student_id')
    # def _onchange_student_id(self):
    #     if self.student_id:
    #         # الخطوة 1: استرجاع المواد المسجلة مسبقًا للطالب
    #         registered_subjects = self.env['student.subject.grade'].search(
    #                 [
    #                         ('student_id', '=', self.student_id.id)
    #                 ]).mapped('subject_id.id')
    #
    #         print(f"Student ID: {self.student_id.id}, Name: {self.student_id.name}")
    #         print(f"Registered Subjects IDs for the student: {registered_subjects}")
    #
    #         # الخطوة 2: المواد المتاحة للطالب
    #         available_subjects = self.student_id.subject_ids.ids
    #         print(f"Available Subjects for the student: {available_subjects}")
    #
    #         # الخطوة 3: إذا كان الطالب ليس لديه مواد، لا تقم بتطبيق أي نطاق
    #         if not available_subjects:
    #             print("No available subjects for this student.")
    #             return {'domain': {'subject_id': []}}
    #
    #         # استبعاد المواد التي تم تسجيلها مسبقًا
    #         filtered_subjects = list(set(available_subjects) - set(registered_subjects))
    #         print(f"Filtered Subjects for the student: {filtered_subjects}")
    #
    #         # التأكد من وجود مواد متاحة للتسجيل
    #         if not filtered_subjects:
    #             print("No subjects left to choose from.")
    #             return {'domain': {'subject_id': [('id', '=', False)]}}
    #
    #         domain = {'subject_id': [('id', 'in', filtered_subjects)]}
    #         print(f"Domain Applied: {domain}")
    #
    #
    #     else:
    #         # الخطوة 2: إذا تم إلغاء تحديد الطالب، قم بحذف اسم المادة
    #         self.subject_id = False  # إلغاء تحديد المادة
    #         # إرجاع نطاق فارغ
    #         domain = {'subject_id': []}
    #
    #     return {'domain': domain}
