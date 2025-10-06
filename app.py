import eventlet
import eventlet.wsgi
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Danh sách mã cổ phiếu bạn muốn theo dõi
SYMBOLS = ["ACB", "VCB", "BID", "CTG", "MBB", "TCB", "VPB", "SSI", "VND", "HCM",
           "FPT", "MWG", "VIC", "VHM", "HPG", "GAS", "SAB", "BVH", "PLX", "VNM"]

API_BASE = "https://vn-stock-api-bsjj.onrender.com/api/stock"

def fetch_price(symbol):
    try:
        r = requests.get(f"{API_BASE}/{symbol}/price", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data
    except Exception as e:
        print(f"Lỗi khi lấy {symbol}: {e}")
    return None

def price_updater():
    while True:
        all_data = {}
        for symbol in SYMBOLS:
            result = fetch_price(symbol)
            if result:
                all_data[symbol] = result.get("data", {})
        if all_data:
            socketio.emit('price_update', all_data)
            print("Đã gửi dữ liệu:", all_data)
        time.sleep(5)  # update mỗi 5 giây

@app.route('/')
def home():
    return jsonify({"status": "WebSocket Server đang chạy 🚀"})

@socketio.on('connect')
def handle_connect():
    print("✅ Client đã kết nối.")
    emit('server_message', {'message': 'Chào mừng tới Stock WebSocket Server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Client ngắt kết nối.")

if __name__ == '__main__':
    thread = threading.Thread(target=price_updater)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=10000)
