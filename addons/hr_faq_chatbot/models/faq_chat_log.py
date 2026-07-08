# -*- coding: utf-8 -*-
from odoo import fields, models


class HrFaqChatLog(models.Model):
    """Một dòng = một lượt hỏi-đáp giữa nhân viên và chatbot nội quy.

    Được ghi lại bởi controllers/main.py mỗi khi có câu hỏi mới, để quản trị
    viên xem lại lịch sử, thống kê câu hỏi thường gặp, và biết chatbot có
    tìm được nguồn tài liệu phù hợp hay không (found_answer = False nghĩa là
    RAG service không tìm thấy đoạn nội quy nào liên quan).
    """

    _name = "hr.faq.chat.log"
    _description = "Lịch sử hỏi đáp - Trợ lý nội quy"
    _order = "create_date desc"
    _rec_name = "question"

    employee_id = fields.Many2one(
        "hr.employee", string="Nhân viên", ondelete="set null"
    )
    user_id = fields.Many2one(
        "res.users", string="Người dùng", default=lambda self: self.env.user
    )
    question = fields.Text(string="Câu hỏi", required=True)
    answer = fields.Text(string="Câu trả lời")
    sources = fields.Text(
        string="Nguồn trích dẫn",
        help="Danh sách tài liệu/mục quy định mà chatbot dùng để trả lời, "
        "một dòng một nguồn.",
    )
    found_answer = fields.Boolean(
        string="Tìm thấy trong quy định",
        default=True,
        help="False nếu RAG service không tìm được đoạn tài liệu nào đủ liên "
        "quan -- các câu hỏi này đáng để rà soát lại kho tài liệu nội quy.",
    )
    response_time_ms = fields.Integer(string="Thời gian phản hồi (ms)")
