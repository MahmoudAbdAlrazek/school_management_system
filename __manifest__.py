{
        'name'       : "School Management System",

        'summary'    : "Short (1 phrase/line) summary of the module's purpose",

        'description': """
Long description of module's purpose
    """,

        'author'     : "My Company",
        'website'    : "https://www.yourcompany.com",

        # Categories can be used to filter modules in modules listing
        # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
        # for the full list
        'category'   : 'Uncategorized',
        'version'    : '0.1',

        # any module necessary for this one to work correctly
        'depends'    : ['base', 'mail'],
        # 'installable': True,
        # 'application': True,

        # always loaded
        'data'       : [
                'security/security_school_student.xml',
                'security/ir.model.access.csv',

                'qweb_reports/report_school_student.xml',

                'views/school_student_views.xml',
                'views/school_classroom_views.xml',
                'views/school_subject_views.xml',
                'views/school_teacher_views.xml',
                'views/student_subject_grade_views.xml',
                'views/student_stage_history_views.xml',
                'views/nationality_views.xml',
                'data/nationality_data.xml',

                'views/base_menu_views.xml'

        ],
        'assets'     : {
                'web.assets_backend' : [
                        'school_management_system/static/src/css/student_subject_grade.css',
                        'school_management_system/static/src/css/font.css',
                        # 'school_management_system/static/src/fonts/NerkoOne-Regular.ttf',
                ],
                'web.assets_frontend': [
                        'school_management_system/static/src/css/student_subject_grade.css',
                        'school_management_system/static/src/css/font.css',
                        # 'school_management_system/static/src/fonts/NerkoOne-Regular.ttf',
                ],
                # 'school_management_system/static/src/fonts/NerkoOne-Regular.ttf'
                #  'school_management_system/static/src/fonts/NerkoOne-Regular.ttf'
                # هذا سيضمن تحميل ملف CSS المخصص في الواجهة الخلفية (backend) والواجهة الأمامية (frontend) لـ Odoo
        },

        # only loaded in demonstration mode
        'demo'       : [
                'demo/demo.xml',
        ],
}
# -*- coding: utf-8 -*-
