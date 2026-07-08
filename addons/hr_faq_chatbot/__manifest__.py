{
    "name": "Trợ lý nội quy (FAQ Chatbot)",
    "version": "15.0.1.0.0",
    "summary": "Chatbot hỏi đáp quy định nội bộ, chính sách công ty, quy trình làm việc (RAG)",
    "description": """
Module này thêm một trợ lý chat cho nhân viên hỏi các câu hỏi về quy định nội bộ,
chính sách công ty và quy trình làm việc. Câu trả lời được sinh ra dựa trên tài liệu
nội quy thực tế của công ty (không phải kiến thức chung), thông qua một service RAG
(Retrieval-Augmented Generation) chạy độc lập bên ngoài Odoo -- xem thư mục
`rag_service/` đi kèm.

Toàn bộ hội thoại được lưu lại trong Odoo (menu Nhân sự > Trợ lý nội quy > Lịch sử hỏi đáp)
để quản trị viên có thể theo dõi, thống kê các câu hỏi thường gặp.
""",
    "category": "Human Resources",
    "author": "Đinh Trường Phong, Đinh Văn Tân Lượng, Nguyễn Đình Tài",
    "depends": ["base", "web", "mail", "hr", "nhan_su"],
    "data": [
        "security/ir.model.access.csv",
        "views/faq_chat_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_faq_chatbot/static/src/css/faq_chatbot.css",
            "hr_faq_chatbot/static/src/js/faq_chatbot.js",
        ],
        "web.assets_qweb": [
            "hr_faq_chatbot/static/src/xml/faq_chatbot_templates.xml",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
