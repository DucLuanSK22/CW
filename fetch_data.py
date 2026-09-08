import requests
import json
import datetime
import os

def update_cw_json():
    url = "https://iboard-query.ssi.com.vn/stock/cw/hose"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://iboard.ssi.com.vn/"
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
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

                ref_price = float(item.get('refPrice', 0) or item.get('priorClosePrice', 0) or 0)
                raw_pct = item.get('priceChangePercent', None) if item.get('priceChangePercent', None) is not None else item.get('changePercent', None)
                if raw_pct is not None:
                    pct_cw = float(raw_pct)
                elif ref_price > 0 and gia_cw > 0:
                    pct_cw = ((gia_cw - ref_price) / ref_price) * 100.0
                else:
                    pct_cw = 0.0

                records.append({
                    'CW': cw_code,
                    'TCPH': issuer,
                    'CK_co_so': underlying,
                    'Gia_CW': gia_cw,
                    'Pct_Change_CW': round(pct_cw, 2),
                    'Tong_KL': tong_kl,
                    'Gia_hien_tai': gia_hien_tai,
                    'Gia_TH': gia_th,
                    'So_ngay_con_lai': max(days_left, 0),
                    'Ti_le_CD_str': ratio_str,
                    'Ti_le_CD_num': ratio_num
                })

            if records:
                out_data = {
                    'updated_at': datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
                    'source': 'SSI iBoard API',
                    'count': len(records),
                    'data': records
                }
                with open('cw_data.json', 'w', encoding='utf-8') as f:
                    json.dump(out_data, f, ensure_ascii=False, indent=2)
                print(f"Successfully generated cw_data.json with {len(records)} items.")
                return True
    except Exception as e:
        print(f"Error fetching SSI data: {e}")

    return False

if __name__ == "__main__":
    update_cw_json()
