# Hướng Dẫn Tích Hợp Gemini AI Chatbot Bảo Mật 100% (Phương Án 1 - Cloudflare Workers Proxy)

Hệ thống đã được tích hợp sẵn giao diện **Gemini AI CW Analyst Chatbot** dạng Floating Widget ở góc trái màn hình.

Để bảo mật **`GEMINI_API_KEY`** 100% không bao giờ bị lộ phía client (Serverless Proxy), bạn thực hiện 3 bước đơn giản sau (Miễn phí 100%):

---

## ⚡ BƯỚC 1: Lấy Gemini API Key Miễn Phí
1. Truy cập [Google AI Studio](https://aistudio.google.com/).
2. Đăng nhập tài khoản Google và bấm **Create API Key**.
3. Copy đoạn mã API Key (dạng `AIzaSy...`).

---

## ☁️ BƯỚC 2: Đẩy Code Proxy Lên Cloudflare Workers (Mất 2 Phút)
1. Đăng nhập hoặc tạo tài khoản miễn phí tại [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Chọn mục **Workers & Pages** ➔ Bấm **Create Application** ➔ Chọn **Create Worker**.
3. Đặt tên cho Worker (ví dụ: `cw-gemini-proxy`) ➔ Bấm **Deploy**.
4. Bấm **Edit Code** ➔ Copy toàn bộ nội dung trong file [cloudflare_worker_proxy.js](file:///c:/Users/luanl/OneDrive/Desktop/II/Investment/CW/cloudflare_worker_proxy.js) trong thư mục dự án và dán đè vào màn hình Cloudflare Worker ➔ Bấm **Save and Deploy**.
5. Quay lại màn hình Worker ➔ Chọn tab **Settings** ➔ **Variables** ➔ Mục **Secret Bindings** ➔ Bấm **Add variable**:
   - **Variable name**: `GEMINI_API_KEY`
   - **Value**: Dán mã Gemini API Key của bạn vào đây.
   - Bấm **Save and Deploy**.

---

## 🔗 BƯỚC 3: Gắn Worker URL Vào Dashboard
1. Copy đường dẫn Worker URL của bạn (VD: `https://cw-gemini-proxy.yourname.workers.dev/api/chat`).
2. Mở Dashboard Web của bạn ([https://ducluansk22.github.io/CW/](https://ducluansk22.github.io/CW/)).
3. Bấm nút **`💬 Gemini AI Tư Vấn CW`** ở góc trái ➔ Bấm biểu tượng ⚙️ (Cấu hình) góc trên bên phải khung chat.
4. Dán URL Worker của bạn vào ô **1. URL Cloudflare Worker Proxy** ➔ Bấm **Lưu Cấu Hình**.

🎉 **Hoàn thành!** Giờ đây bạn và bất kỳ ai truy cập web đều có thể chat với Gemini AI để phân tích chứng quyền real-time mà **Gemini API Key của bạn hoàn toàn nằm an toàn trên Cloudflare Server**!
