/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, useState } = owl;

/**
 * Client action "Trợ lý nội quy" -- Phiên bản tối ưu hóa hoàn chỉnh cho Odoo 15 (OWL 1)
 */
class FaqChatbot extends Component {
    setup() {
        this.rpc = useService("rpc");

        // Khởi tạo trạng thái dữ liệu cho khung chat
        this.state = useState({
            messages: [
                {
                    role: "bot",
                    text: "Xin chào, tôi là trợ lý nội quy. Bạn có thể hỏi tôi về chính sách công ty, quy trình làm việc, nghỉ phép...",
                    sources: [],
                },
            ],
            input: "",
            loading: false,
        });
    }

    /**
     * Hàm vòng đời của OWL 1 - Tự động chạy SAU KHI GIAO DIỆN ĐÃ RENDER XONG XUÔI
     * Giúp tự động cuộn mượt mà xuống đáy mỗi khi có tin nhắn mới mà không sợ bị lỗi undefined refs.
     */
    patched() {
        if (this.refs && this.refs.chatContainer) {
            this.refs.chatContainer.scrollTop = this.refs.chatContainer.scrollHeight;
        }
    }

    // Cập nhật giá trị ô input khi người dùng nhập liệu
    onInputChange(ev) {
        this.state.input = ev.target.value;
    }

    // Xử lý gửi câu hỏi sang Backend Odoo -> FastAPI
    async sendQuestion() {
        const question = this.state.input.trim();
        if (!question || this.state.loading) {
            return;
        }

        // 1. Đẩy câu hỏi của User vào danh sách (Hàm patched() sẽ tự cuộn xuống)
        this.state.messages.push({ role: "user", text: question, sources: [] });
        this.state.input = ""; // Xóa trắng ô nhập liệu
        this.state.loading = true;

        try {
            // 2. Gọi API đến Controller Odoo
            const result = await this.rpc("/hr_faq_chatbot/ask", { question });
            
            // 3. Nhận kết quả từ RAG service và hiển thị lên màn hình
            this.state.messages.push({
                role: "bot",
                text: result.answer,
                sources: result.sources || [],
            });
        } catch (error) {
            // Xử lý khi mất kết nối mạng hoặc server FastAPI sập
            this.state.messages.push({
                role: "bot",
                text: "Đã xảy ra lỗi khi kết nối với trợ lý nội quy. Vui lòng kiểm tra lại dịch vụ hoặc thử lại sau.",
                sources: [],
            });
        } finally {
            this.state.loading = false;
        }
    }

    // Bắt sự kiện gõ phím Enter để gửi nhanh
    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendQuestion();
        }
    }
}

// Gắn giao diện XML vào Component
FaqChatbot.template = "hr_faq_chatbot.ChatbotTemplate";

// Đăng ký Client Action chính thức vào hệ thống Odoo 15
registry.category("actions").add("hr_faq_chatbot.chat_action", FaqChatbot);

export default FaqChatbot;