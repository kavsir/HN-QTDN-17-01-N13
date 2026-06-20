# -*- coding: utf-8 -*-
{
    'name': "Quản lý khách hàng và Công việc",
    'summary': "Phân hệ Quản lý khách hàng tích hợp Quản lý công việc và HRM - Nhóm 13",
    'description': """
        Đề tài Nhóm 13: Đinh Trường Phong, Đinh Văn Tân Lượng.
        Tích hợp phân hệ CRM và Project/Task dựa trên dữ liệu gốc từ HRM.
    """,
    'author': "Nhóm 13 - FIT-DNU",
    'website': "https://ttdn1501.aiotlabdnu.xyz/web",
    'category': 'Sales/CRM',
    'version': '0.1',
    'license': 'LGPL-3',

    # Module bắt buộc phải có để hệ thống chạy đúng dữ liệu gốc nhân sự
    'depends': ['base', 'nhan_su', 'quan_ly_cong_viec'], # BẮT BUỘC phải có 'quan_ly_cong_viec' ở đây
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        'views/co_hoi.xml',
        'views/menu.xml',
    ],
}