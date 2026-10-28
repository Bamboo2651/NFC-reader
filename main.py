import time

from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.System import readers


SEPARATOR = "=" * 50


def clear_screen():
    """ターミナルの表示を消して、左上へカーソルを戻す。"""
    print("\033[2J\033[H", end="")


def print_header(title):
    print(SEPARATOR)
    print(title)
    print(SEPARATOR)


def show_waiting_screen(reader_name):
    clear_screen()
    print_header("NFCカードリーダー")
    print("\n状態: 待機中")
    print("使用機器:", reader_name)
    print("\nカードをかざしてください")
    print("終了: Ctrl+C")


def show_reader_missing_screen():
    clear_screen()
    print_header("NFCカードリーダー")
    print("\n状態: リーダー未接続")
    print("\nRC-S300をPCへ接続してください")
    print("終了: Ctrl+C")


def read_card(connection):
    """接続済みのNFCカードからUIDとNDEFテキストを読み取る。"""
    get_uid_command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    uid_data, uid_sw1, uid_sw2 = connection.transmit(get_uid_command)

    if uid_sw1 != 0x90 or uid_sw2 != 0x00:
        print("UIDの取得に失敗しました")
        return

    uid = " ".join(f"{byte:02X}" for byte in uid_data)
    print("\n[カード情報]")
    print("UID:", uid)

    first_read_command = [0xFF, 0xB0, 0x00, 0x04, 0x10]
    card_data, card_sw1, card_sw2 = connection.transmit(first_read_command)

    if card_sw1 != 0x90 or card_sw2 != 0x00:
        print("カードのデータを読み取れませんでした")
        return

    print("\n[NDEFデータ]")

    if len(card_data) < 2 or card_data[0] != 0x03:
        print("NDEF形式のデータではありません")
        return

    ndef_length = card_data[1]
    if ndef_length == 0:
        print("カードにNDEFデータは保存されていません")
        return

    total_length = 2 + ndef_length + 1
    block_count = (total_length + 15) // 16
    all_data = []

    for block_index in range(block_count):
        start_page = 4 + block_index * 4
        read_command = [0xFF, 0xB0, 0x00, start_page, 0x10]
        block_data, block_sw1, block_sw2 = connection.transmit(read_command)

        if block_sw1 != 0x90 or block_sw2 != 0x00:
            print(f"ページ{start_page}からの読み取りに失敗しました")
            return

        all_data.extend(block_data)

    ndef_record = all_data[2:2 + ndef_length]
    if len(ndef_record) < 5 or ndef_record[3] != 0x54:
        print("テキスト形式ではないNDEFデータです")
        return

    payload_length = ndef_record[2]
    status_byte = ndef_record[4]
    language_length = status_byte & 0x3F
    text_start = 5 + language_length
    text_end = 4 + payload_length
    text_bytes = bytes(ndef_record[text_start:text_end])

    try:
        decoded_text = text_bytes.decode("utf-8")
    except UnicodeDecodeError:
        print("保存された文字をUTF-8として読み取れませんでした")
        return

    print("種類: テキスト")
    print("データ長:", ndef_length, "バイト")
    print("内容:", decoded_text)


def main():
    current_reader_name = None
    reader_missing_announced = False

    try:
        while True:
            reader_list = readers()

            if not reader_list:
                if not reader_missing_announced:
                    show_reader_missing_screen()
                    reader_missing_announced = True
                current_reader_name = None
                time.sleep(1)
                continue

            reader_missing_announced = False
            reader = reader_list[0]
            reader_name = str(reader)

            if reader_name != current_reader_name:
                show_waiting_screen(reader_name)
                current_reader_name = reader_name

            connection = reader.createConnection()
            connected = False

            try:
                connection.connect()
                connected = True

                clear_screen()
                print_header("NFCカード読み取り結果")
                print("\n状態: 読み取り完了")
                print("使用機器:", reader_name)
                read_card(connection)
                print("\n" + SEPARATOR)
                print("カードを離してください")
                print("終了: Ctrl+C")

                # 同じカードを何度も読まないよう、離されるまで待つ。
                while True:
                    time.sleep(0.3)
                    connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])

            except (NoCardException, CardConnectionException):
                # 読み取り後にカードが離されたときだけ、待機画面へ戻す。
                if connected:
                    show_waiting_screen(reader_name)

            finally:
                if connected:
                    try:
                        connection.disconnect()
                    except CardConnectionException:
                        pass

            time.sleep(0.4)

    except KeyboardInterrupt:
        print("\n読み取りを終了しました")


if __name__ == "__main__":
    main()
