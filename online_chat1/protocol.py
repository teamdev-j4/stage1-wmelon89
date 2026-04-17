# protocol.py

MAX_PACKET_SIZE = 4096
MAX_USERNAME_IN_BYTES = 255

#username, message をbyte型のデータに変換する関数
def build_packet(username: str, message: str) -> bytes:
    username_bytes = username.encode("utf-8")
    message_bytes = message.encode("utf-8")

    if len(username_bytes) > MAX_USERNAME_IN_BYTES:
        raise ValueError("Username is too long. It must be 255 bytes or less.")

#パケットの組み立て。先頭はユーザ名のバイト数
    packet = bytes([len(username_bytes)]) + username_bytes + message_bytes

#パケットサイズのチェック
    if len(packet) > MAX_PACKET_SIZE:
        raise ValueError("Packet is too large. Must be 4096 bytes or less.")
#パケットをリターン
    return packet

#受け取ったバイト列を元のusernameとmessageに戻す関数
def parse_packet(data: bytes) -> tuple[str, str]:
#受け取ったデータが空かどうかチェック
    if not data:
        raise ValueError("Empty packet")

    username_len = data[0]
#データが短すぎないかをチェック
    if len(data) < 1 + username_len:
        raise ValueError("Invalid packet format")
#username、messageを切り出す
    username_bytes = data[1:1 + username_len]
    message_bytes = data[1 + username_len:]

#バイトから文字列への変換
    username = username_bytes.decode("utf-8")
    message = message_bytes.decode("utf-8")

#usernameとmessageをリターン
    return username, message