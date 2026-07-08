# -*- coding: utf-8 -*-
import logging
import time

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Đổi mặc định này bằng System Parameter 'hr_faq_chatbot.rag_service_url'
# (Settings > Technical > System Parameters) khi triển khai thật -- ví dụ
# "http://rag-service:8000/ask" nếu chạy trong cùng docker-compose network.
DEFAULT_RAG_URL = "http://10.0.2.2:8000/ask" # Hoặc "http://host.docker.internal:8000/ask"
DEFAULT_TIMEOUT = 20  # giây -- LLM + tìm kiếm vector có thể mất vài giây


class HrFaqChatbotController(http.Controller):

    @http.route(
        "/hr_faq_chatbot/ask",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def ask(self, question, **kwargs):
        """Nhận câu hỏi từ widget chat (static/src/js/faq_chatbot.js), forward
        sang RAG service bên ngoài, ghi log, và trả kết quả về cho trình duyệt.

        Trả về luôn (không raise) ngay cả khi RAG service lỗi/không phản hồi,
        để giao diện chat luôn hiển thị được một câu trả lời/hoặc thông báo
        lỗi rõ ràng cho người dùng thay vì crash.
        """
        question = (question or "").strip()
        if not question:
            return {"answer": "Bạn chưa nhập câu hỏi.", "sources": [], "found_answer": False}

        icp = request.env["ir.config_parameter"].sudo()
        rag_url = icp.get_param("hr_faq_chatbot.rag_service_url", DEFAULT_RAG_URL)
        timeout = int(icp.get_param("hr_faq_chatbot.rag_service_timeout", DEFAULT_TIMEOUT))

        start = time.time()
        answer = None
        sources = []
        found_answer = False

        try:
            resp = requests.post(rag_url, json={"question": question}, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            found_answer = bool(data.get("found_answer", bool(sources)))
        except requests.exceptions.RequestException as exc:
            _logger.error("[hr_faq_chatbot] RAG service không phản hồi: %s", exc)
            answer = (
                "Xin lỗi, trợ lý nội quy hiện không kết nối được tới hệ thống "
                "tra cứu tài liệu. Vui lòng thử lại sau hoặc liên hệ phòng "
                "nhân sự."
            )

        elapsed_ms = int((time.time() - start) * 1000)

        employee = request.env.user.employee_id
        request.env["hr.faq.chat.log"].sudo().create(
            {
                "employee_id": employee.id if employee else False,
                "user_id": request.env.user.id,
                "question": question,
                "answer": answer,
                "sources": "\n".join(sources) if sources else False,
                "found_answer": found_answer,
                "response_time_ms": elapsed_ms,
            }
        )

        return {"answer": answer, "sources": sources, "found_answer": found_answer}
