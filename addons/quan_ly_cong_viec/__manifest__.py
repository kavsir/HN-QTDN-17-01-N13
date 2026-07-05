{
    'name': "Quản lý công việc",
    'summary': "Phân hệ độc lập Quản lý công việc - Nhóm 13",
    'author': "Nhóm 13 - FIT-DNU",
    'website': "https://ttdn1501.aiotlabdnu.xyz/web",
    'category': 'Sales/CRM',
    'version': '0.1',
    'license': 'LGPL-3',

    'depends': ['base', 'nhan_su','mail'],
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/cong_viec.xml',  
    ],
}