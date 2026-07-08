# Module Odoo 15: Trợ lý nội quy (hr_faq_chatbot)

## Cài đặt

1. Copy thư mục `hr_faq_chatbot` vào thư mục addons của Odoo (ví dụ
   `/opt/odoo/custom-addons/hr_faq_chatbot`).
2. Khởi động lại Odoo với addons-path trỏ tới thư mục đó (hoặc thêm vào
   `addons_path` trong `odoo.conf`).
3. Vào **Apps**, bật "Developer mode" (Settings > General Settings > cuối
   trang), bấm **Update Apps List**, tìm "Trợ lý nội quy (FAQ Chatbot)" và
   **Install**.
4. Cấu hình URL của RAG service (xem `rag_service/README.md` mục 4).
5. Vào menu **Nhân sự > Trợ lý nội quy > Hỏi đáp** để dùng thử.

## Cấu trúc module

```
hr_faq_chatbot/
  __manifest__.py
  models/faq_chat_log.py       -- lưu lịch sử hỏi đáp
  controllers/main.py          -- endpoint /hr_faq_chatbot/ask, gọi RAG service
  views/faq_chat_views.xml     -- menu, action, view lịch sử
  static/src/js/faq_chatbot.js -- giao diện chat (OWL component)
  static/src/xml/...           -- template QWeb cho giao diện chat
  static/src/css/...           -- style giao diện chat
```

## Luồng hoạt động

1. Nhân viên mở menu "Hỏi đáp", gõ câu hỏi.
2. `faq_chatbot.js` gọi `POST /hr_faq_chatbot/ask`.
3. `controllers/main.py` forward câu hỏi sang RAG service (cấu hình qua
   System Parameter `hr_faq_chatbot.rag_service_url`).
4. RAG service tìm đoạn tài liệu liên quan + gọi Groq LLM sinh câu trả lời,
   trả về `{answer, sources, found_answer}`.
5. Controller lưu lại toàn bộ vào `hr.faq.chat.log` và trả kết quả về giao
   diện.
6. Quản trị viên (nhóm `hr.group_hr_manager`) xem lại lịch sử tại menu
   "Lịch sử hỏi đáp" -- hữu ích để biết câu hỏi nào chưa có tài liệu trả lời
   (`found_answer = False`), từ đó bổ sung tài liệu nội quy.

## Lưu ý bảo mật

- Route `/hr_faq_chatbot/ask` yêu cầu đăng nhập (`auth="user"`), chỉ nhân
  viên đã login mới hỏi được.
- Nếu RAG service chạy trên máy/server khác, nên đặt sau firewall nội bộ
  hoặc thêm xác thực (ví dụ shared secret header) giữa Odoo và service --
  bản hiện tại kết nối trực tiếp qua HTTP nội bộ, phù hợp cho đồ án/demo.
