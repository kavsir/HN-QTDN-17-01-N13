{
    'name': "Quản lý công việc",
    'summary': "Phân hệ Quản lý dự án & Quản lý công việc liên kết HRM - Nhóm 13",
    'author': "Nhóm 13 - FIT-DNU",
    'website': "https://ttdn1501.aiotlabdnu.xyz/web",
    'category': 'Services/Project',
    'version': '0.2',
    'license': 'LGPL-3',

    'depends': ['base', 'mail', 'nhan_su'],
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/cong_viec.xml',
    ],
}