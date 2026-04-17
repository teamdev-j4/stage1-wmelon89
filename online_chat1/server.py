# server.py

import socket
import threading
import time

#protocol.pyからparse_packet()をimport する
from protocol import parse_packet

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
BUFFER_SIZE = 4096
#Time Out を60秒に設定
CLIENT_TIMEOUT = 60
#5秒毎に切断対象となるChatがないか確認
CLEANUP_INTERVAL = 5

# クライアント情報を保存する場所を辞書形式で確保{(ip, port): {"username": str, "last_seen(クライアントが最後にサーバにメッセージを送った時刻)": float}}
clients = {}
#スレッドの排他制御。複数のスレッドが同時にClientsを触るのを防ぐ
clients_lock = threading.Lock()

#inactive なクライアントを削除
def cleanup_inactive_clients():
    while True:
        #CLEANUP_INTERVALの間だけ待つ
        time.sleep(CLEANUP_INTERVAL)
        #現在時刻を取得
        now = time.time()
        #最後の通信から時間が経ちすぎているものをチェックし、TIMEOUTよりもinactiveな時間が大きいクライアントをリストに入れる
        with clients_lock:
            inactive_clients = [
                addr for addr, info in clients.items()
                if now - info["last_seen"] > CLIENT_TIMEOUT
            ]
        #リストに入ったクライアントを削除
            for addr in inactive_clients:
                username = clients[addr]["username"]
                del clients[addr]
                print(f"[INFO] Removed inactive client: {username} {addr}")

#メッセージを中継するリレー関数
def relay_message(sock: socket.socket, sender_addr: tuple[str, int], data: bytes):
    with clients_lock:
        for client_addr in clients: #接続中の全クライアントをループ
            if client_addr != sender_addr:#送信者本人には送らない
                try:#受信したデータをそのまま他のクライアントへ送信
                    sock.sendto(data, client_addr)
                except OSError as e:#送信失敗時のエラーログ
                    print(f"[ERROR] Failed to send to {client_addr}: {e}")


def main():#UDPでメッセージを送受信するソケットの作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #IPv4かつUDP
    #ポートへのバインド処理
    sock.bind((SERVER_HOST, SERVER_PORT))
    #サーバの起動を表示
    print(f"[INFO] UDP server started on {SERVER_HOST}:{SERVER_PORT}")
    #cleanup用のスレッドの作成　main プログラムが終了したらこのスレッドも終了
    cleanup_thread = threading.Thread(target=cleanup_inactive_clients, daemon=True)
    #cleanup用スレッドの起動
    cleanup_thread.start()

    while True:
        try:
            #UDPでデータの受信（データ、送信元アドレス）
            data, addr = sock.recvfrom(BUFFER_SIZE)
            #受信データをユーザ名とメッセージに分解
            username, message = parse_packet(data)
            #Clients辞書を更新する
            with clients_lock:#withでclientsを安全に更新するために排他制御する
                clients[addr] = {
                    "username": username,
                    "last_seen": time.time()#最終送信時刻
                }
            #サーバ側に確認用のログを出す
            print(f"[RECV] {username}@{addr}: {message}")
            #他のクライアントに中継する
            relay_message(sock, addr, data)
        #例外処理
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()