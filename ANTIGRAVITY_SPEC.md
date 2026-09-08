# Antigravity Project Specification: Vietnamese Stock Warrant (CW) Valuation & Ranking Dashboard

## 1. Project Overview & Objective
Build an automated, real-time web application to analyze, rank, and track Vietnamese covered warrants (Chứng quyền có bảo đảm - CW).
The application fetches market data directly via API, computes quantitative metrics based on a custom 5-star rating system, and displays 3 primary tables with a 1-click "Copy Tab-Separated to Clipboard" feature for direct pasting into Microsoft Excel.

## 2. Technology Stack
- **Backend / Calculation Engine**: Python 3.10+ (FastAPI or Streamlit)
- **Data Fetching**: `requests`, `aiohttp` (calling SSI iBoard API: `https://iboard-query.ssi.com.vn/stock/cw/hose`)
- **Data Manipulation**: `pandas`, `numpy`
- **Frontend**: Streamlit (fastest for financial dashboards) or React/Next.js + TailwindCSS
- **Output Format**: Clean UI Table + TSV (Tab-Separated Values) format for clipboard export

---

## 3. Core Quantitative Methodology (5-Star Rating System)

### A. Moneyness & Breakeven Calculations
- **Break-even Price (VND)**:
  `Diem_hoa_von = Gia_TH + (Gia_CW * Ti_le_CD_num)`
- **% to Break-even**:
  `Pct_to_breakeven = ((Diem_hoa_von - Gia_hien_tai) / Gia_hien_tai) * 100`
- **% In-The-Money (Pct_to_ITM)**:
  `Pct_to_ITM = ((Gia_hien_tai - Gia_TH) / Gia_hien_tai) * 100`

### B. Leverage Metrics (Gearing & Effective Gearing)
- **Raw Gearing**:
  `Gearing = Gia_hien_tai / (Gia_CW * Ti_le_CD_num)`
- **Delta Estimation ($\Delta$)**:
  - `Pct_to_ITM >= 10%`: $\Delta = 0.85$
  - `5% <= Pct_to_ITM < 10%`: $\Delta = 0.75$
  - `0% <= Pct_to_ITM < 5%`: $\Delta = 0.60$
  - `-3% <= Pct_to_ITM < 0%`: $\Delta = 0.50$
  - `-7% <= Pct_to_ITM < -3%`: $\Delta = 0.38$
  - `-12% <= Pct_to_ITM < -7%`: $\Delta = 0.25$
  - `Pct_to_ITM < -12%`: $\Delta = 0.10$
- **Effective Gearing ($\Omega$)**:
  `Effective_Gearing = Delta_Est * Gearing`

### C. 5-Star Scoring Breakdown (Scale: 1 to 5 for each criterion)
1. **Moneyness Score (`S1`)**:
   - $\ge 5\%$: 5 | $\ge 0\%$: 4 | $\ge -5\%$: 3 | $\ge -10\%$: 2 | $< -10\%$: 1
2. **Time Runway Score (`S2`)**:
   - $\ge 180$ days: 5 | $\ge 120$ days: 4 | $\ge 90$ days: 3 | $\ge 45$ days: 2 | $< 45$ days: 1
3. **Breakeven Distance Score (`S3`)**:
   - $\le 5\%$: 5 | $\le 10\%$: 4 | $\le 15\%$: 3 | $\le 20\%$: 2 | $> 20\%$: 1
4. **Conversion Ratio Concentration Score (`S4`)**:
   - $\le 2.05$: 5 | $\le 3.05$: 4 | $\le 4.05$: 3 | $\le 6.05$: 2 | $> 6.05$: 1
5. **Liquidity Score (`S5`)**:
   - $\ge 1,000,000$: 5 | $\ge 500,000$: 4 | $\ge 200,000$: 3 | $\ge 50,000$: 2 | $< 50,000$: 1
- **Average Total Score (`Diem_TB`)**:
  `Diem_TB = (S1 + S2 + S3 + S4 + S5) / 5.0`

---

## 4. Required Output Tables

### Table 1: Top 50 Market Leaders (Top 50 Toàn Thị Trường)
- **Filter**: `So_ngay_con_lai >= 10`, `Gia_CW > 0`, `Tong_KL >= 10,000`. Deduplicated by unique `CW`.
- **Sort**: `Diem_TB` (descending), `Tong_KL` (descending), `Pct_to_breakeven` (ascending).
- **Limit**: 50 rows.

### Table 2: User Portfolio Tracking (Đánh giá CW đang nắm giữ)
- **Monitored Codes**: `['CMBB2614', 'CVPB2615', 'CACB2511', 'CTCB2611', 'CACB2606', 'CMWG2616', 'CHPG2607']`
- **Sort**: `Diem_TB` (descending), `Tong_KL` (descending).
- **Actionable Flag**:
  - `So_ngay_con_lai < 20` and `Pct_to_ITM > 0`: "Cảnh báo chốt lời"
  - `So_ngay_con_lai < 20` and `Pct_to_ITM < -10%`: "Báo động cắt lỗ khẩn cấp"

### Table 3: Top 10 Explosive Growth Candidates (Top 10 Tiềm năng nhất)
- **Filter**:
  - `So_ngay_con_lai >= 50`
  - `Tong_KL >= 100,000`
  - `Ti_le_CD_num <= 3.5`
  - `Pct_to_ITM >= -8.0%`
  - `Diem_TB >= 3.4`
- **Sort**: `Effective_Gearing` (descending), `Tong_KL` (descending).
- **Limit**: 10 rows.

---

## 5. TSV Export Formatting Specification (For Direct Excel Paste)
Columns must follow this exact order:
`Xếp hạng\tMã CW\tTCPH\tCơ sở (Giá TT)\tThị giá CW\tTrạng thái (Moneyness)\tGiá TH\tTỉ lệ CĐ\tThời gian còn lại\tTổng KL\tĐiểm TB`

Formatting rules:
- `Thị giá CW`: rounded integer + "đ" (e.g., `760đ`)
- `Giá TH`: rounded integer + "đ" (e.g., `20825đ`)
- `Cơ sở (Giá TT)`: formatted as `{SYMBOL} ({PRICE/1000:.2f}k)` (e.g., `MBB (20.20k)`)
- `Trạng thái`: `ITM (+{diff:.2f}k)`, `OTM ({diff:.2f}k)`, or `ATM (0.00k)`
- `Thời gian còn lại`: `{DAYS} ngày`
- `Tổng KL`: comma-separated integers (e.g., `1,600,500`)
- `Điểm TB`: `{SCORE:.1f} ⭐`
