import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import io

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Hệ Thống Phân Tích & Định Giá Chứng Quyền (CW) - SSI Market",
    page_icon="📈",
    layout="wide"
)

# Custom High-End Modern CSS Styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0b0e14;
        color: #e0e6ed;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #131b2e 0%, #1c253b 100%);
        border: 1px solid #2a3652;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        font-size: 26px;
        font-weight: 800;
        color: #38ef7d;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* KPI Summary Cards */
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .kpi-card {
        flex: 1;
        background: #141c2e;
        border: 1px solid #23314d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .kpi-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }

    .kpi-val {
        font-size: 24px;
        font-weight: 700;
        color: #60a5fa;
    }
    
    .kpi-lbl {
        font-size: 13px;
        color: #94a3b8;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Custom Styled Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #162032;
        border: 1px solid #24324d;
        border-radius: 8px 8px 0px 0px;
        padding: 12px 24px;
        color: #94a3b8;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border-color: #3b82f6 !important;
        color: #ffffff !important;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }

    /* Export Box Styling */
    .export-box {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

USER_HOLDINGS = ['CMBB2614', 'CVPB2615', 'CACB2511', 'CTCB2611', 'CACB2606', 'CMWG2616', 'CHPG2607']

def fetch_ssi_data():
    """Direct fetch from SSI iBoard API with error handling."""
    url = "https://iboard-query.ssi.com.vn/stock/cw/hose"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://iboard.ssi.com.vn/"
    }
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            raw_json = res.json().get('data', {})
            cw_list = raw_json.get('coveredWarrantData', [])
            underlying_list = raw_json.get('underlyingData', [])

            underlying_prices = {}
            for u in underlying_list:
                sym = u.get('stockSymbol')
                price = u.get('matchedPrice', 0) or u.get('refPrice', 0) or u.get('priorClosePrice', 0) or 0
                underlying_prices[sym] = float(price)

            today = datetime.datetime.now()
            records = []
            for item in cw_list:
                cw_code = item.get('stockSymbol')
                issuer = item.get('issuerName', 'N/A')
                underlying = item.get('underlyingSymbol', 'N/A')
                gia_cw = float(item.get('matchedPrice', 0) or item.get('refPrice', 0) or item.get('priorClosePrice', 0) or 0)
                tong_kl = float(item.get('nmTotalTradedQty', 0) or item.get('stockVol', 0) or 0)
                gia_hien_tai = underlying_prices.get(underlying, 0.0)
                gia_th = float(item.get('exercisePrice', 0) or 0)

                ratio_str = item.get('exerciseRatio', '1:1') or '1:1'
                try:
                    if ':' in ratio_str:
                        parts = ratio_str.split(':')
                        ratio_num = float(parts[0]) / float(parts[1])
                    else:
                        ratio_num = float(ratio_str)
                except Exception:
                    ratio_num = 1.0

                mat_str = item.get('maturityDate', '')
                days_left = 0
                if mat_str:
                    try:
                        mat_dt = datetime.datetime.strptime(mat_str, '%d/%m/%Y')
                        days_left = (mat_dt - today).days
                    except Exception:
                        pass

                records.append({
                    'CW': cw_code,
                    'TCPH': issuer,
                    'CK_co_so': underlying,
                    'Gia_CW': gia_cw,
                    'Tong_KL': tong_kl,
                    'Gia_hien_tai': gia_hien_tai,
                    'Gia_TH': gia_th,
                    'So_ngay_con_lai': max(days_left, 0),
                    'Ti_le_CD_str': ratio_str,
                    'Ti_le_CD_num': ratio_num
                })

            if records:
                return pd.DataFrame(records)
    except Exception as e:
        st.warning(f"Không thể gọi SSI API trực tiếp: {e}. Đang dùng dữ liệu dự phòng.")

    # Mock Data Fallback
    mock_records = [
        {'CW': 'CMBB2614', 'TCPH': 'KIS', 'CK_co_so': 'MBB', 'Gia_CW': 760, 'Tong_KL': 1600500, 'Gia_hien_tai': 20200, 'Gia_TH': 20825, 'So_ngay_con_lai': 45, 'Ti_le_CD_str': '2:1', 'Ti_le_CD_num': 2.0},
        {'CW': 'CVPB2615', 'TCPH': 'SSI', 'CK_co_so': 'VPB', 'Gia_CW': 1200, 'Tong_KL': 850000, 'Gia_hien_tai': 19500, 'Gia_TH': 18000, 'So_ngay_con_lai': 110, 'Ti_le_CD_str': '2.5:1', 'Ti_le_CD_num': 2.5},
        {'CW': 'CACB2511', 'TCPH': 'SSI', 'CK_co_so': 'ACB', 'Gia_CW': 1450, 'Tong_KL': 345000, 'Gia_hien_tai': 22300, 'Gia_TH': 19832, 'So_ngay_con_lai': 13, 'Ti_le_CD_str': '1.7245:1', 'Ti_le_CD_num': 1.7245},
        {'CW': 'CTCB2611', 'TCPH': 'VCSC', 'CK_co_so': 'TCB', 'Gia_CW': 2100, 'Tong_KL': 1250000, 'Gia_hien_tai': 24000, 'Gia_TH': 21000, 'So_ngay_con_lai': 190, 'Ti_le_CD_str': '2:1', 'Ti_le_CD_num': 2.0},
        {'CW': 'CACB2606', 'TCPH': 'HSC', 'CK_co_so': 'ACB', 'Gia_CW': 890, 'Tong_KL': 1424200, 'Gia_hien_tai': 22300, 'Gia_TH': 24000, 'So_ngay_con_lai': 120, 'Ti_le_CD_str': '3.4491:1', 'Ti_le_CD_num': 3.4491},
        {'CW': 'CMWG2616', 'TCPH': 'KIS', 'CK_co_so': 'MWG', 'Gia_CW': 1850, 'Tong_KL': 2100000, 'Gia_hien_tai': 68000, 'Gia_TH': 62000, 'So_ngay_con_lai': 95, 'Ti_le_CD_str': '4:1', 'Ti_le_CD_num': 4.0},
        {'CW': 'CHPG2607', 'TCPH': 'MBS', 'CK_co_so': 'HPG', 'Gia_CW': 310, 'Tong_KL': 450000, 'Gia_hien_tai': 27000, 'Gia_TH': 31000, 'So_ngay_con_lai': 15, 'Ti_le_CD_str': '3:1', 'Ti_le_CD_num': 3.0},
    ]
    return pd.DataFrame(mock_records)

def evaluate_cw(df):
    """Calculates quantitative metrics & 5-star rating system."""
    if df.empty:
        return df
    df = df.copy()

    df['Diem_hoa_von_vnd'] = df['Gia_TH'] + (df['Gia_CW'] * df['Ti_le_CD_num'])
    df['Pct_to_breakeven'] = (df['Diem_hoa_von_vnd'] - df['Gia_hien_tai']) / np.maximum(df['Gia_hien_tai'], 1.0) * 100
    df['Pct_to_ITM'] = (df['Gia_hien_tai'] - df['Gia_TH']) / np.maximum(df['Gia_hien_tai'], 1.0) * 100

    def get_phan_loai(p):
        if p > 5.0: return "ITM sâu"
        elif p > 0.0: return "ITM nhẹ"
        elif p == 0.0: return "ATM"
        elif p >= -5.0: return "OTM nhẹ"
        return "OTM sâu"

    df['Phan_loai_Moneyness'] = df['Pct_to_ITM'].apply(get_phan_loai)
    df['Gearing'] = df['Gia_hien_tai'] / np.maximum(df['Gia_CW'] * df['Ti_le_CD_num'], 1.0)

    def get_delta(p):
        if p >= 10: return 0.85
        elif p >= 5: return 0.75
        elif p >= 0: return 0.60
        elif p >= -3: return 0.50
        elif p >= -7: return 0.38
        elif p >= -12: return 0.25
        return 0.10

    df['Delta_Est'] = df['Pct_to_ITM'].apply(get_delta)
    df['Effective_Gearing'] = df['Delta_Est'] * df['Gearing']

    s1 = df['Pct_to_ITM'].apply(lambda p: 5 if p >= 5 else (4 if p >= 0 else (3 if p >= -5 else (2 if p >= -10 else 1))))
    s2 = df['So_ngay_con_lai'].apply(lambda d: 5 if d >= 180 else (4 if d >= 120 else (3 if d >= 90 else (2 if d >= 45 else 1))))
    s3 = df['Pct_to_breakeven'].apply(lambda b: 5 if b <= 5 else (4 if b <= 10 else (3 if b <= 15 else (2 if b <= 20 else 1))))
    s4 = df['Ti_le_CD_num'].apply(lambda r: 5 if r <= 2.05 else (4 if r <= 3.05 else (3 if r <= 4.05 else (2 if r <= 6.05 else 1))))
    s5 = df['Tong_KL'].apply(lambda k: 5 if k >= 1000000 else (4 if k >= 500000 else (3 if k >= 200000 else (2 if k >= 50000 else 1))))

    df['Diem_TB'] = (s1 + s2 + s3 + s4 + s5) / 5.0

    def get_action_flag(row):
        days = row['So_ngay_con_lai']
        itm = row['Pct_to_ITM']
        if days < 20 and itm > 0:
            return "⚠️ Cảnh báo chốt lời"
        elif days < 20 and itm < -10:
            return "🚨 Báo động cắt lỗ khẩn cấp"
        return "✅ An toàn"

    df['Khuyen_nghi'] = df.apply(get_action_flag, axis=1)
    return df

def to_tsv(df_subset):
    """Original TSV string format specification for Excel copy-paste."""
    lines = ["Xếp hạng\tMã CW\tTCPH\tCơ sở (Giá TT)\tThị giá CW\tTrạng thái (Moneyness)\t% Moneyness\tGiá TH\tTỉ lệ CĐ\tThời gian còn lại\tTổng KL\tĐiểm TB"]
    for idx, r in df_subset.reset_index(drop=True).iterrows():
        diff = (r['Gia_hien_tai'] - r['Gia_TH']) / 1000.0
        m_str = f"ITM (+{diff:.2f}k)" if diff > 0 else (f"OTM ({diff:.2f}k)" if diff < 0 else "ATM (0.00k)")
        pct_itm_str = f"{r['Pct_to_ITM']:+.2f}%"
        row_vals = [
            f"TOP {idx + 1}",
            str(r['CW']),
            str(r['TCPH']),
            f"{r['CK_co_so']} ({r['Gia_hien_tai']/1000:.2f}k)",
            f"{r['Gia_CW']:.0f}đ",
            m_str,
            pct_itm_str,
            f"{r['Gia_TH']:.0f}đ",
            str(r['Ti_le_CD_str']),
            f"{r['So_ngay_con_lai']:.0f} ngày",
            f"{r['Tong_KL']:,.0f}",
            f"{r['Diem_TB']:.1f} ⭐"
        ]
        lines.append("\t".join(row_vals))
    return "\n".join(lines)

def to_excel_bytes(df_subset, tab_name="CW_Analysis"):
    """Generates Excel binary file (.xlsx) for download."""
    export_df = pd.DataFrame()
    for idx, r in df_subset.reset_index(drop=True).iterrows():
        diff = (r['Gia_hien_tai'] - r['Gia_TH']) / 1000.0
        m_str = f"ITM (+{diff:.2f}k)" if diff > 0 else (f"OTM ({diff:.2f}k)" if diff < 0 else "ATM (0.00k)")
        pct_itm_str = f"{r['Pct_to_ITM']:+.2f}%"
        export_df = pd.concat([export_df, pd.DataFrame([{
            'Xếp hạng': f"TOP {idx + 1}",
            'Mã CW': str(r['CW']),
            'TCPH': str(r['TCPH']),
            'Cơ sở (Giá TT)': f"{r['CK_co_so']} ({r['Gia_hien_tai']/1000:.2f}k)",
            'Thị giá CW': f"{r['Gia_CW']:.0f}đ",
            'Trạng thái (Moneyness)': m_str,
            '% Moneyness': pct_itm_str,
            'Giá TH': f"{r['Gia_TH']:.0f}đ",
            'Tỉ lệ CĐ': str(r['Ti_le_CD_str']),
            'Thời gian còn lại': f"{r['So_ngay_con_lai']:.0f} ngày",
            'Tổng KL': r['Tong_KL'],
            'Điểm TB': f"{r['Diem_TB']:.1f} ⭐"
        }])], ignore_index=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, sheet_name=tab_name, index=False)
    return output.getvalue()

# --- INITIALIZE SESSION STATE FOR MANUAL API REFRESH ---
if 'cw_df' not in st.session_state or 'last_updated' not in st.session_state:
    with st.spinner("Đang khởi tạo dữ liệu thị trường SSI..."):
        raw_df = fetch_ssi_data()
        st.session_state['cw_df'] = evaluate_cw(raw_df)
        st.session_state['last_updated'] = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

# --- APP UI HEADER & MANUAL REFRESH CONTROL ---
st.markdown("""
<div class="header-card">
    <h1 class="header-title">⚡ HỆ THỐNG PHÂN TÍCH & ĐỊNH GIÁ CHỨNG QUYỀN (CW)</h1>
    <div class="header-subtitle">Mô hình định giá 5-sao & Đòn bẩy thực tế (Effective Gearing) | Nguồn dữ liệu: <b>SSI iBoard API</b></div>
</div>
""", unsafe_allow_html=True)

# Top Bar Controls: Refresh Button & Status
ctrl_col1, ctrl_col2 = st.columns([1, 2])

with ctrl_col1:
    if st.button("🔄 CẬP NHẬT DỮ LIỆU TỪ SÀN (SSI)", type="primary", use_container_width=True):
        with st.spinner("Đang kết nối SSI API kéo dữ liệu mới nhất từ Sàn..."):
            raw_df = fetch_ssi_data()
            st.session_state['cw_df'] = evaluate_cw(raw_df)
            st.session_state['last_updated'] = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
            st.toast("✅ Đã cập nhật thành công dữ liệu trực tiếp từ Sàn!", icon="🎉")

with ctrl_col2:
    st.info(f"🕒 **Lần cập nhật gần nhất:** `{st.session_state['last_updated']}` *(Chỉ gọi API khi bấm nút Cập nhật để tránh lag/treo)*")

st.markdown("<br>", unsafe_allow_html=True)

# Main Data Pipeline
cw_df = st.session_state['cw_df']
if not cw_df.empty:
    unique_cw = cw_df.sort_values(by=['Tong_KL'], ascending=False).drop_duplicates(subset=['CW'])

    # KPI Analytics Cards
    itm_count = (unique_cw['Pct_to_ITM'] > 0).sum()
    avg_score = unique_cw['Diem_TB'].mean()
    top_volume_cw = unique_cw.iloc[0]['CW'] if not unique_cw.empty else "N/A"

    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-val">{len(unique_cw):,}</div>
            <div class="kpi-lbl">Mã CW Niêm Yết</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color: #10b981;">{itm_count} ({itm_count/max(len(unique_cw), 1)*100:.1f}%)</div>
            <div class="kpi-lbl">Mã ITM (Có Lãi)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color: #f59e0b;">{avg_score:.2f} ⭐</div>
            <div class="kpi-lbl">Điểm TB Thị Trường</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color: #ec4899;">{top_volume_cw}</div>
            <div class="kpi-lbl">CW Thanh Khoản Nhất</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Main Interactive Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📌 1. ĐÁNH GIÁ DANH MỤC NẮM GIỮ",
        "⚡ 2. TOP 10 TIỀM NĂNG TĂNG GIÁ (EFFECTIVE GEARING)",
        "🏆 3. TOP 50 CHỨNG QUYỀN HÀNG ĐẦU THỊ TRƯỜNG",
        "🌐 4. TOÀN BỘ CHỨNG QUYỀN TRÊN SÀN (ALL CW)"
    ])

    # Helper Renderer for Table + Filter Controls + Export Options
    def render_tab_content(subset_df, title, desc, tab_key):
        st.subheader(title)
        st.caption(desc)

        # Multi-Column & Universal Search Controls Panel
        with st.expander("🎛️ **BỘ LỌC CHI TIẾT TỪNG CỘT & TÌM KIẾM TOÀN BỘ BẢNG**", expanded=True):
            # Row 1: Universal Search + Text/Select Filters
            r1_1, r1_2, r1_3, r1_4 = st.columns([2, 1, 1, 1])
            with r1_1:
                search_query = st.text_input("🔎 Tìm kiếm TẤT CẢ các cột:", key=f"global_search_{tab_key}", placeholder="Nhập Mã, Giá, TCPH, Điểm...").strip().upper()
            with r1_2:
                f_cw = st.text_input("🏷️ Lọc Mã CW:", key=f"fcw_{tab_key}", placeholder="Mã CW...").strip().upper()
            with r1_3:
                issuers = ["Tất cả"] + sorted(list(subset_df['TCPH'].unique())) if not subset_df.empty else ["Tất cả"]
                f_tcph = st.selectbox("🏢 Lọc TCPH:", issuers, key=f"ftcph_{tab_key}")
            with r1_4:
                underlyings = ["Tất cả"] + sorted(list(subset_df['CK_co_so'].unique())) if not subset_df.empty else ["Tất cả"]
                f_ck = st.selectbox("📈 Lọc CK Cơ Sở:", underlyings, key=f"fck_{tab_key}")

            # Row 2: Price & Moneyness Numeric Filters
            r2_1, r2_2, r2_3, r2_4 = st.columns(4)
            with r2_1:
                f_mon_status = st.selectbox("💰 % Moneyness:", ["Tất cả", "ITM (Có lãi > 0%)", "OTM (Chưa lãi <= 0%)"], key=f"fmon_{tab_key}")
            with r2_2:
                f_min_gcw = st.number_input("💵 Giá CW Min (đ):", value=0, step=100, key=f"fmin_gcw_{tab_key}")
            with r2_3:
                f_max_gcw = st.number_input("💵 Giá CW Max (đ):", value=0, step=100, key=f"fmax_gcw_{tab_key}")
            with r2_4:
                f_min_score = st.slider("⭐ Điểm TB Min:", 1.0, 5.0, 1.0, 0.1, key=f"fscore_{tab_key}")

            # Row 3: Runway, Volume & Conversion Ratio Filters
            r3_1, r3_2, r3_3, r3_4 = st.columns(4)
            with r3_1:
                f_min_days = st.number_input("⏳ Ngày Còn Lai Min:", value=0, step=5, key=f"fdays_{tab_key}")
            with r3_2:
                f_min_vol = st.number_input("📊 Tổng KL Min:", value=0, step=50000, key=f"fvol_{tab_key}")
            with r3_3:
                f_max_ratio = st.number_input("🔄 Tỉ lệ CĐ Max:", value=0.0, step=0.5, key=f"fratio_{tab_key}")
            with r3_4:
                f_min_gcs = st.number_input("🏛️ Giá Cơ Sở Min (đ):", value=0, step=1000, key=f"fgcs_{tab_key}")

            if st.button("🧹 XÓA TẤT CẢ BỘ LỌC & TÌM KIẾM", key=f"reset_{tab_key}", type="secondary", use_container_width=True):
                for k in [f"global_search_{tab_key}", f"fcw_{tab_key}", f"ftcph_{tab_key}", f"fck_{tab_key}", f"fmon_{tab_key}", f"fmin_gcw_{tab_key}", f"fmax_gcw_{tab_key}", f"fscore_{tab_key}", f"fdays_{tab_key}", f"fvol_{tab_key}", f"fratio_{tab_key}", f"fgcs_{tab_key}"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        # Apply All Filters
        filtered_df = subset_df.copy()

        # Universal Search
        if search_query:
            def matches_all_cols(row):
                row_str = " ".join([str(val) for val in row.values]).upper()
                return search_query in row_str
            filtered_df = filtered_df[filtered_df.apply(matches_all_cols, axis=1)]

        # Individual Column Filters
        if f_cw:
            filtered_df = filtered_df[filtered_df['CW'].str.contains(f_cw, na=False)]

        if f_tcph != "Tất cả":
            filtered_df = filtered_df[filtered_df['TCPH'] == f_tcph]

        if f_ck != "Tất cả":
            filtered_df = filtered_df[filtered_df['CK_co_so'] == f_ck]

        if f_mon_status == "ITM (Có lãi > 0%)":
            filtered_df = filtered_df[filtered_df['Pct_to_ITM'] > 0]
        elif f_mon_status == "OTM (Chưa lãi <= 0%)":
            filtered_df = filtered_df[filtered_df['Pct_to_ITM'] <= 0]

        if f_min_gcw > 0:
            filtered_df = filtered_df[filtered_df['Gia_CW'] >= f_min_gcw]

        if f_max_gcw > 0:
            filtered_df = filtered_df[filtered_df['Gia_CW'] <= f_max_gcw]

        if f_min_gcs > 0:
            filtered_df = filtered_df[filtered_df['Gia_hien_tai'] >= f_min_gcs]

        if f_min_days > 0:
            filtered_df = filtered_df[filtered_df['So_ngay_con_lai'] >= f_min_days]

        if f_min_vol > 0:
            filtered_df = filtered_df[filtered_df['Tong_KL'] >= f_min_vol]

        if f_max_ratio > 0:
            filtered_df = filtered_df[filtered_df['Ti_le_CD_num'] <= f_max_ratio]

        if f_min_score > 1.0:
            filtered_df = filtered_df[filtered_df['Diem_TB'] >= f_min_score]

        st.markdown(f"**Kết Quả Hiển Thị:** `{len(filtered_df)}` / `{len(subset_df)}` mã chứng quyền")

        # Formatted Display Table
        disp = pd.DataFrame()
        disp['STT'] = [f"#{i+1}" for i in range(len(filtered_df))]
        disp['Mã CW'] = filtered_df['CW']
        disp['TCPH'] = filtered_df['TCPH']
        disp['CK Cơ Sở'] = filtered_df['CK_co_so']
        disp['Giá CW'] = filtered_df['Gia_CW'].apply(lambda p: f"{p:,.0f}đ")
        disp['Giá Cơ Sở'] = filtered_df['Gia_hien_tai'].apply(lambda p: f"{p:,.0f}đ")
        disp['Giá TH'] = filtered_df['Gia_TH'].apply(lambda p: f"{p:,.0f}đ")
        disp['% Moneyness'] = filtered_df['Pct_to_ITM'].apply(lambda p: f"+{p:.2f}%" if p > 0 else f"{p:.2f}%")
        disp['Phân Loại'] = filtered_df['Phan_loai_Moneyness']
        disp['Tỉ lệ CĐ'] = filtered_df['Ti_le_CD_str']
        disp['Ngày Còn Lai'] = filtered_df['So_ngay_con_lai'].apply(lambda d: f"{d:.0f} ngày")
        disp['Tổng KL'] = filtered_df['Tong_KL'].apply(lambda k: f"{k:,.0f}")
        disp['Điểm TB ⭐'] = filtered_df['Diem_TB'].apply(lambda s: f"{s:.1f} ⭐")

        if 'Effective_Gearing' in filtered_df.columns:
            disp['Đòn Bẩy Thực (Ω)'] = filtered_df['Effective_Gearing'].apply(lambda g: f"{g:.2f}x")

        if 'Khuyen_nghi' in filtered_df.columns:
            disp['Khuyến Nghị'] = filtered_df['Khuyen_nghi']

        st.dataframe(disp, use_container_width=True, hide_index=True)

        # Export & Copy Options Section
        st.markdown("---")
        st.markdown("### 📥 XUẤT DỮ LIỆU & COPY VÀO EXCEL")
        
        ex_col1, ex_col2 = st.columns([1, 1])
        with ex_col1:
            tsv_text = to_tsv(filtered_df)
            st.markdown("**1-Click Copy Snippet (Chuẩn Tab-Separated cho Excel):**")
            st.text_area(label="Dữ liệu TSV", value=tsv_text, height=140, key=f"tsv_{tab_key}")

        with ex_col2:
            st.markdown("**Xuất File Trực Tiếp:**")
            excel_bytes = to_excel_bytes(filtered_df, tab_name=tab_key)
            st.download_button(
                label="📊 Tải File Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"{tab_key}_CW_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_xls_{tab_key}",
                type="primary",
                use_container_width=True
            )
            
            csv_bytes = tsv_text.replace('\t', ',').encode('utf-8-sig')
            st.download_button(
                label="📄 Tải File CSV (.csv)",
                data=csv_bytes,
                file_name=f"{tab_key}_CW_Report.csv",
                mime="text/csv",
                key=f"dl_csv_{tab_key}",
                use_container_width=True
            )

    with tab1:
        if 'user_holdings' not in st.session_state:
            st.session_state['user_holdings'] = USER_HOLDINGS.copy()

        st.markdown("### 📌 Quản Lý Danh Mục Chứng Quyền Nắm Giữ")
        all_available_cw = sorted(list(unique_cw['CW'].unique()))
        selected_holdings = st.multiselect(
            "➕ **Thêm / Bớt Mã CW Trong Danh Mục Nắm Giữ:**",
            options=all_available_cw,
            default=[cw for cw in st.session_state['user_holdings'] if cw in all_available_cw],
            key="holdings_multiselect"
        )
        if selected_holdings != st.session_state['user_holdings']:
            st.session_state['user_holdings'] = selected_holdings
            st.rerun()

        hold_df = unique_cw[unique_cw['CW'].isin(st.session_state['user_holdings'])].sort_values(by=['Diem_TB', 'Tong_KL'], ascending=[False, False])
        render_tab_content(
            hold_df,
            "📌 1. Danh Mục Chứng Quyền Đang Nắm Giữ",
            "Đánh giá chi tiết tình trạng mã CW monitored và các cảnh báo hành động (Chốt lời / Cắt lỗ / An toàn)",
            "Holdings"
        )

    with tab2:
        pot_df = unique_cw[
            (unique_cw['So_ngay_con_lai'] >= 50) &
            (unique_cw['Tong_KL'] >= 100000) &
            (unique_cw['Ti_le_CD_num'] <= 3.5) &
            (unique_cw['Pct_to_ITM'] >= -8.0) &
            (unique_cw['Diem_TB'] >= 3.4)
        ].sort_values(by=['Effective_Gearing', 'Tong_KL'], ascending=[False, False]).head(10)
        render_tab_content(
            pot_df,
            "⚡ 2. Top 10 CW Tiềm Năng Tăng Giá Cao Nhất (Effective Gearing)",
            "Bộ lọc: Ngày còn lại ≥ 50, Tổng KL ≥ 100,000, Tỉ lệ CĐ ≤ 3.5, Moneyness ≥ -8.0%, Điểm TB ≥ 3.4 | Sắp xếp theo Đòn bẩy thực tế (Effective Gearing)",
            "Top10_Growth"
        )

    with tab3:
        viable = unique_cw[(unique_cw['So_ngay_con_lai'] >= 10) & (unique_cw['Gia_CW'] > 0) & (unique_cw['Tong_KL'] >= 10000)]
        top50_df = viable.sort_values(by=['Diem_TB', 'Tong_KL', 'Pct_to_breakeven'], ascending=[False, False, True]).head(50)
        render_tab_content(
            top50_df,
            "🏆 3. Top 50 Chứng Quyền Tốt Nhất Toàn Thị Trường",
            "Bộ lọc: Ngày còn lại ≥ 10, Giá CW > 0, Tổng KL ≥ 10,000 | Sắp xếp theo Điểm TB ↓, Thanh Khoản ↓, % Đến Hòa Vốn ↑",
            "Top50_Market"
        )

    with tab4:
        all_cw_sorted = unique_cw.sort_values(by=['Diem_TB', 'Tong_KL'], ascending=[False, False])
        render_tab_content(
            all_cw_sorted,
            "🌐 4. Toàn Bộ Chứng Quyền Niêm Yết Trên Sàn Chứng Khoán",
            "Tra cứu toàn bộ danh sách chứng quyền niêm yết với công cụ tìm kiếm tất cả các cột",
            "All_CW"
        )
