from flask import Flask
from flask_socketio import SocketIO
import requests, time, threading, os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ====== CẤU HÌNH ======
STOCK_SYMBOLS = [
    "ACB", "VCB", "FPT", "VNM", "HPG", "SSI", "MWG", "VIC", "BID", "CTG",
    "TCB", "GAS", "MBB", "PLX", "NVL", "VRE", "STB", "SAB", "POW", "VHM"
]
UPDATE_INTERVAL = 5   # thời gian cập nhật (giây)
API_BASE = "https://vn-stock-api-bsjj.onrender.com/api/stock"

# ====== KHỞI TẠO SERVER ======
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "✅ Stock WebSocket Bridge đang hoạt động!"

# ====== LẤY DỮ LIỆU CHO 1 MÃ ======
def fetch_symbol(symbol):
    url = f"{API_BASE}/{symbol}/price"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("success"):
            return symbol, data["data"]
        else:
            return symbol, {"error": "API error"}
    except Exception as e:
        return symbol, {"error": str(e)}

# ====== LẤY DỮ LIỆU SONG SONG ======
def fetch_all_stocks():
    all_data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_symbol, sym): sym for sym in STOCK_SYMBOLS}
        for future in as_completed(futures):
            symbol, data = future.result()
            all_data[symbol] = data
    return all_data

# ====== LUỒNG CHÍNH PHÁT DỮ LIỆU ======
def background_task():
    while True:
        all_data = fetch_all_stocks()
        socketio.emit("stock_update", all_data)
        print(f"🔄 Đã gửi dữ liệu {len(all_data)} mã cổ phiếu.")
        time.sleep(UPDATE_INTERVAL)

# ====== SỰ KIỆN WEBSOCKET ======
@socketio.on('connect')
def handle_connect():
    print("✅ Client đã kết nối.")

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Client ngắt kết nối.")

# ====== CHẠY SERVER ======
if __name__ == '__main__':
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
