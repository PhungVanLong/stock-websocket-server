from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import requests, threading, time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

SYMBOLS = ["ACB", "VCB", "BID", "CTG", "MBB", "TCB", "VPB", "SSI", "VND", "HCM",
           "FPT", "MWG", "VIC", "VHM", "HPG", "GAS", "SAB", "BVH", "PLX", "VNM"]
API_BASE = "https://vn-stock-api-bsjj.onrender.com/api/stock"

def fetch_price(symbol):
    try:
        r = requests.get(f"{API_BASE}/{symbol}/price", timeout=5)
        if r.status_code == 200:
            return r.json().get("data", {})
    except Exception as e:
        print(f"Lỗi khi lấy {symbol}: {e}")
    return {}

def price_updater():
    while True:
        data = {sym: fetch_price(sym) for sym in SYMBOLS}
        socketio.emit("price_update", data)
        print("Đã gửi:", data)
        time.sleep(5)

@app.route('/')
def index():
    return jsonify({"status": "WebSocket Server đang chạy 🚀"})

@socketio.on('connect')
def handle_connect():
    print("✅ Client đã kết nối.")
    emit("server_message", {"message": "Chào mừng tới Stock WebSocket Server!"})

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Client ngắt kết nối.")

if __name__ == "__main__":
    threading.Thread(target=price_updater, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=10000)
