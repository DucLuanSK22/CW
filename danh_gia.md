# Phương Pháp Đánh Giá Sao (& Mô Hình Định Lượng CW)

Hệ thống Phân Tích & Định Giá Chứng Quyền (Covered Warrants - CW) sử dụng **Phương pháp Đánh giá Định lượng Đa Tiêu chí (Multi-Criteria Quantitative Scoring Framework)** để tự động chấm điểm xếp hạng từ **1.0 đến 5.0 sao (⭐)** cho từng mã chứng quyền đang giao dịch trên thị trường.

Điểm tổng sắp (**`Điểm TB ⭐`**) là trung bình cộng của **5 trụ cột chỉ số thành phần** (mỗi chỉ số được chấm từ 1 đến 5 sao dựa trên dữ liệu realtime của SSI iBoard):

$$\text{Điểm TB} = \frac{S_1 + S_2 + S_3 + S_4 + S_5}{5}$$

---

## 📊 Chi Tiết 5 Trụ Cột Đánh Giá Thành Phần ($S_1 \to S_5$)

### 1. Tiêu chí $S_1$: Trạng thái Moneyness (% Trạng thái Lời/Lỗ)
Đo lường khoảng cách từ thị giá của cổ phiếu cơ sở tới giá thực hiện của chứng quyền:

$$\% \text{Moneyness} = \frac{\text{Giá Cơ Sở} - \text{Giá Thực Hiện}}{\text{Giá Cơ Sở}} \times 100\%$$

| Điểm Sao ($S_1$) | Điều Kiện $\% \text{Moneyness}$ | Phân Loại | Diễn Giải Ý Nghĩa |
| :---: | :--- | :--- | :--- |
| **5 ⭐** | $\% \text{Moneyness} > +5.0\%$ | `1. ITM sâu` | Vượt xa giá thực hiện, chứng quyền có nội giá (intrinsic value) rất cao, rủi ro thấp. |
| **4 ⭐** | $0.0\% < \% \text{Moneyness} \le +5.0\%$ | `2. ITM nhẹ` | Vừa chớm vượt giá thực hiện, chứng quyền đang có lãi nhẹ. |
| **3 ⭐** | $\% \text{Moneyness} == 0.0\%$ | `3. ATM` | Giá cơ sở xấp xỉ bằng giá thực hiện. |
| **3 ⭐** | $-5.0\% \le \% \text{Moneyness} < 0.0\%$ | `4. OTM nhẹ` | Trạng thái lỗ nhẹ dưới 5%. |
| **1-2 ⭐** | $\% \text{Moneyness} < -5.0\%$ | `5. OTM sâu` | Lỗ sâu trên 5%, giá cơ sở còn xa giá thực hiện, áp lực mất giá cao. |

---

### 2. Tiêu chí $S_2$: Thời Gian Còn Lại Đến Ngày Đáo Hạn
Thời gian đáo hạn là yếu tố quyết định tốc độ suy giảm giá trị thời gian (Theta Decay). Chứng quyền có thời hạn dài giúp nhà đầu tư giảm thiểu rủi ro bị mất trắng tiền bản quyền khi thị trường đi ngang:

| Điểm Sao ($S_2$) | Số Ngày Còn Lại | Đánh Giá Rủi Ro Theta |
| :---: | :--- | :--- |
| **5 ⭐** | $\ge 180$ ngày ($> 6$ tháng) | An toàn tuyệt đối về mặt thời gian, biến độngTheta rất nhỏ. |
| **4 ⭐** | $120 \le \text{Ngày} < 180$ ngày ($4 - 6$ tháng) | An toàn cao, đủ thời gian cho cổ phiếu cơ sở bứt phá. |
| **3 ⭐** | $90 \le \text{Ngày} < 120$ ngày ($3 - 4$ tháng) | Mức trung bình, phù hợp sóng ngắn hạn. |
| **2 ⭐** | $45 \le \text{Ngày} < 90$ ngày ($1.5 - 3$ tháng) | Cần bắt đầu chú ý nhịp suy giảm giá trị. |
| **1 ⭐** | $< 45$ ngày | **Rủi ro cao**: Tốc độ bào mòn giá trị thời gian diễn ra rất nhanh. |

---

### 3. Tiêu chí $S_3$: Phần Trăm Tới Điểm Hòa Vốn (% Breakeven)
Chỉ số này đại diện cho mức tăng trưởng tối thiểu mà cổ phiếu cơ sở cần đạt được tại ngày đáo hạn để nhà đầu tư đạt điểm hòa vốn (sau khi trừ chi phí bản quyền mua CW):

$$\text{Điểm Hòa Vốn (VNĐ)} = \text{Giá Thực Hiện} + (\text{Giá CW} \times \text{Tỉ Lệ Chuyển Đổi})$$

$$\% \text{Breakeven} = \frac{\text{Điểm Hòa Vốn} - \text{Giá Cơ Sở}}{\text{Giá Cơ Sở}} \times 100\%$$

| Điểm Sao ($S_3$) | Điều Kiện $\% \text{Breakeven}$ | Đánh Giá Khả Năng Hòa Vốn |
| :---: | :--- | :--- |
| **5 ⭐** | $\le 5.0\%$ | Cực kỳ dễ đạt hòa vốn và sinh lời. |
| **4 ⭐** | $5.0\% < \% \text{Breakeven} \le 10.0\%$ | Khả thi cao trong các nhịp tăng của tài sản cơ sở. |
| **3 ⭐** | $10.0\% < \% \text{Breakeven} \le 15.0\%$ | Yêu cầu cổ phiếu cơ sở tăng trưởng khá. |
| **2 ⭐** | $15.0\% < \% \text{Breakeven} \le 20.0\%$ | Khó khăn, đòi hỏi sóng tăng mạnh. |
| **1 ⭐** | $> 20.0\%$ | Quá xa điểm hòa vốn, áp lực tăng giá cực lớn. |

---

### 4. Tiêu chí $S_4$: Tỉ Lệ Chuyển Đổi (Conversion Ratio)
Tỉ lệ chuyển đổi phản ánh số lượng chứng quyền cần thiết để đổi lấy 1 cổ phiếu cơ sở. Tỉ lệ nhỏ hơn giúp giá chứng quyền biến động nhạy hơn và bám sát biến động cổ phiếu cơ sở:

| Điểm Sao ($S_4$) | Tỉ Lệ Chuyển Đổi (CĐ) | Đặc Điểm Biến Động Giá |
| :---: | :--- | :--- |
| **5 ⭐** | Tỉ lệ $\le 2.05 : 1$ | Biến động rất nhạy theo giá cổ phiếu cơ sở. |
| **4 ⭐** | $2.05 < \text{Tỉ lệ} \le 3.05 : 1$ | Nhạy tốt, biên độ giá rõ ràng. |
| **3 ⭐** | $3.05 < \text{Tỉ lệ} \le 4.05 : 1$ | Mức trung bình thị trường. |
| **2 ⭐** | $4.05 < \text{Tỉ lệ} \le 6.05 : 1$ | Biến động giá nhỏ theo từng bước giá. |
| **1 ⭐** | Tỉ lệ $> 6.05 : 1$ | Tỉ lệ quá lớn, biến động giá chậm. |

---

### 5. Tiêu chí $S_5$: Thanh Khoản Thị Trường (Volume)
Tổng khối lượng giao dịch khớp lệnh trong phiên thể hiện khả năng mua/bán dễ dàng mà không gây ra hiện tượng trượt giá (Slippage):

| Điểm Sao ($S_5$) | Khối Lượng Khớp Lệnh (Phiên) | Trạng Thái Thanh Khoản |
| :---: | :--- | :--- |
| **5 ⭐** | $\ge 1.000.000$ CW | **Thanh khoản cực mạnh**, dễ dàng giải ngân & chốt lời lớn. |
| **4 ⭐** | $500.000 \le \text{KL} < 1.000.000$ CW | Thanh khoản dồi dào. |
| **3 ⭐** | $200.000 \le \text{KL} < 500.000$ CW | Thanh khoản trung bình, đủ cho quy mô nhỏ. |
| **2 ⭐** | $50.000 \le \text{KL} < 200.000$ CW | Thanh khoản thấp, cần chú ý khi mua/bán. |
| **1 ⭐** | $< 50.000$ CW | **Thanh khoản kém**, rủi ro kẹt hàng khi muốn chốt lỗ. |

---

## 🏆 Thang Điểm Tổng Hợp & Chiến Lược Đầu Tư

| Thang Điểm ⭐ | Đánh Giá Tự Động | Khuyến Nghị Chiến Lược |
| :---: | :--- | :--- |
| **4.5 - 5.0 ⭐** | 🌟 **Rất Tiềm Năng** | Chứng quyền ưu tú: Vị thế ITM sâu/nhẹ, thời hạn dài ($>4$ tháng), thanh khoản cao, % Breakeven thấp. Thích hợp cho danh mục nắm giữ chủ lực. |
| **3.5 - 4.4 ⭐** | ✅ **Tốt / An Toàn** | Cân bằng tuyệt vời giữa đòn bẩy và độ an toàn. Thích hợp cho các nhịp lướt sóng đòn bẩy ngắn - trung hạn. |
| **3.0 - 3.4 ⭐** | ⚖️ **Trung Bình** | Cần theo dõi sát xu hướng cổ phiếu cơ sở trước khi mở vị thế. |
| **< 3.0 ⭐** | ⚠️ **Rủi Ro Cao** | Thường là chứng quyền sắp đáo hạn ($<20$ ngày) hoặc OTM sâu. Nên cân nhắc cắt lỗ hoặc loại khỏi danh mục. |

---

## ⚡ Các Chỉ Số Định Lượng Khác Trong Hệ Thống

1. **Đòn Bẩy Thực (Effective Gearing $\Omega$):**
   $$\Omega = \text{Delta} \times \text{Gearing} = \text{Delta} \times \left( \frac{\text{Giá Cơ Sở}}{\text{Giá CW} \times \text{Tỉ Lệ CĐ}} \right)$$
   *Trong đó Delta được ước tính dựa trên trạng thái % Moneyness ($0.10 \to 0.85$).*

2. **Cờ Cảnh Báo Tự Động (Action Flag):**
   - ⚠️ **Cảnh báo chốt lời**: Khi chứng quyền sắp đáo hạn ($< 20$ ngày) và đang ở trạng thái ITM ($> 0\%$).
   - 🚨 **Báo động cắt lỗ khẩn cấp**: Khi chứng quyền sắp đáo hạn ($< 20$ ngày) và lỗ sâu (OTM $< -10\%$).

3. **🛡️ QUY TẮC KHÓA ĐIỂM BẢO VỆ TÀI KHOẢN:**
   Khi chứng quyền còn dưới 30 ngày đáo hạn VÀ đang lỗ sâu ($\text{OTM} < -10\%$):
   - **Ép trần điểm số tối đa:** $\text{Điểm TB} = \min(\text{Điểm TB}, 1.5 ⭐)$
   - **Nhãn khuyến nghị khẩn cấp:** `🚨 RỦI RO MẤT TRẮNG`
   
   ```python
   # Logic khóa điểm bảo vệ tài khoản:
   if row['So_ngay_con_lai'] < 30 and row['Pct_to_ITM'] < -10:
       row['Diem_TB'] = min(row['Diem_TB'], 1.5)  # Ép trần tối đa không quá 1.5 ⭐
       row['Khuyen_nghi'] = "🚨 RỦI RO MẤT TRẮNG"
   ```
