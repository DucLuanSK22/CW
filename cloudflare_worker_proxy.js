/**
 * Cloudflare Worker Proxy for Gemini 1.5 Flash API
 * 
 * Instructions:
 * 1. Go to https://dash.cloudflare.com/ -> Workers & Pages -> Create Worker
 * 2. Paste this code into the Worker editor.
 * 3. Go to Worker Settings -> Variables -> Secret Binding -> Add variable:
 *    Name: GEMINI_API_KEY
 *    Value: <Your_Gemini_API_Key_From_AI_Studio>
 * 4. Click Save and Deploy!
 * 5. Copy your Worker URL (e.g., https://cw-gemini-proxy.yourname.workers.dev/api/chat)
 *    and paste it into the Chatbot Settings in the CW Dashboard.
 */

export default {
  async fetch(request, env) {
    // Enable CORS for frontend requests
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }

    try {
      const apiKey = env.GEMINI_API_KEY;
      if (!apiKey) {
        return new Response(JSON.stringify({ error: "GEMINI_API_KEY is not configured in Worker Secrets." }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      const body = await request.json();
      const userMessage = body.message || "";
      const cwContext = body.cw_context || [];

      // Construct system instruction with market context
      const systemInstruction = `Bạn là Antigravity CW AI Financial Analyst - Chuyên gia tư vấn phân tích Chứng Quyền (Covered Warrants) thuộc thị trường chứng khoán Việt Nam.
Trả lời ngắn gọn, súc tích, chuyên nghiệp bằng tiếng Việt.

DỮ LIỆU THỊ TRƯỜNG CHỨNG QUYỀN ĐANG HIỂN THỊ TRÊN BẢNG (SSI Realtime Data):
${JSON.stringify(cwContext.slice(0, 35), null, 2)}

NHIỆM VỤ CỦA BẠN:
1. Dựa trên dữ liệu thị trường ở trên để đưa ra đánh giá, phân tích hoặc trả lời câu hỏi của nhà đầu tư.
2. Nêu rõ lý do dựa trên: % Moneyness, Phân Loại (1. ITM sâu -> 5. OTM sâu), Điểm TB ⭐, Đòn Bẩy Thực (Effective Gearing), Số ngày còn lại.
3. Cảnh báo rủi ro nếu chứng quyền sắp đáo hạn (<20 ngày) hoặc quá xa trạng thái hòa vốn.`;

      const candidateUrls = [
        `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${apiKey}`,
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`
      ];

      const payload = {
        contents: [
          {
            role: "user",
            parts: [
              { text: `${systemInstruction}\n\nCÂU HỎI CỦA NHÀ ĐẦU TƯ: ${userMessage}` }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.4,
          maxOutputTokens: 1000
        }
      };

      let geminiData = null;
      let lastError = null;

      for (const gUrl of candidateUrls) {
        try {
          const geminiRes = await fetch(gUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          if (geminiRes.ok) {
            geminiData = await geminiRes.json();
            break;
          } else {
            const errJson = await geminiRes.json().catch(() => ({}));
            lastError = errJson.error?.message || `HTTP ${geminiRes.status}`;
          }
        } catch (e) {
          lastError = e.message;
        }
      }

      if (!geminiData) {
        throw new Error(`Tất cả mô hình Gemini đều phản hồi lỗi: ${lastError}`);
      }

      const replyText = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || "Không thể lấy phản hồi từ Gemini API.";

      return new Response(JSON.stringify({ reply: replyText }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });

    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
  }
};
