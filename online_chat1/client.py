# client.py

import socket
import threading
from protocol import build_packet, parse_packet

SERVER_HOST = "127.0.0.1" #自分自身を指すアドレス。サーバーもクライアントも自分のPCだから。
SERVER_PORT = 8000
BUFFER_SIZE = 4096

#サーバからのデータ受信処理
def receive_messages(sock: socket.socket):
    while True:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)  #_は送信元アドレス。今回は不要なので無視する
            username, message = parse_packet(data) #データをユーザ名とメッセージに分解
            print(f"\n[{username}] {message}")
            print("> ", end="", flush=True) #"プロンプト"＞"を改行しないですぐに表示
        except Exception as e: #エラーが出たらエラー内容を変数eに入れてエラーメッセ―ジを表示
            print(f"\n[ERROR] Receiving message failed: {e}")
            break #受信ループ終了


def main():
    username = input("Enter your username: ").strip() #strip()で入力データの余白を削除
    if not username:
        print("Username cannot be empty.")
        return
    #ソケットの作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #AF_INET, SOCK_DGRAMはソケットの性質を決める指定値
    #socket.socket: socketモジュールの中のsocketクラスを利用して、socketオブジェクトを生成。sockはインスタンス

    #受信スレッドを別スレッドで同時に動かす。threadingは並行処理を行うための標準モジュール
    receive_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True) #Threadにあとで実行する関数としてreceive_messageを渡す。
    #args=(sock,)はreceive_messagesに渡す引数をタプルで指定。daemon=Trueはメインが終わったら自動終了する設定
    
    #受信スレッド開始
    receive_thread.start()

    print("Type your messages. Press Ctrl+C to exit.")

    while True:
        try:
            message = input("> ").strip()
            if not message:
                continue

            packet = build_packet(username, message)
            sock.sendto(packet, (SERVER_HOST, SERVER_PORT))

        except ValueError as e:
            print(f"[ERROR] {e}")
        except KeyboardInterrupt:
            print("\nExiting chat.")
            break
        except Exception as e:
            print(f"[ERROR] Sending message failed: {e}")
            break

    sock.close()


if __name__ == "__main__":
    main()