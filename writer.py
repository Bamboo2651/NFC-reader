from urllib.parse import urlparse

from smartcard.Exceptions import NoCardException
from smartcard.System import readers


URI_PREFIXES = (
    ("https://www.", 0x02),
    ("http://www.", 0x01),
    ("https://", 0x04),
    ("http://", 0x03),
)


def select_record_type():
    """書き込むNDEFレコードの種類を選ぶ。"""
    print("書き込むデータの種類を選んでください")
    print("1: テキスト")
    print("2: URL")

    while True:
        selection = input("選択 (1/2): ").strip()
        if selection in {"1", "2"}:
            return selection
        print("1または2を入力してください")


def normalize_url(value):
    """Web URLをNDEF URIレコード向けの形式に整える。"""
    url = value.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("正しいWebサイトのURLを入力してください")

    return url


def create_text_record(text):
    """UTF-8のNDEF Textレコードを作る。"""
    text_bytes = list(text.encode("utf-8"))
    language_code = list("ja".encode("ascii"))
    status_byte = len(language_code)
    payload = [status_byte] + language_code + text_bytes
    return create_ndef_record(0x54, payload)


def create_uri_record(url):
    """Web URLのNDEF URIレコードを作る。"""
    prefix_code = 0x00
    uri_body = url

    for prefix, code in URI_PREFIXES:
        if url.lower().startswith(prefix):
            prefix_code = code
            uri_body = url[len(prefix):]
            break

    payload = [prefix_code] + list(uri_body.encode("utf-8"))
    return create_ndef_record(0x55, payload)


def create_ndef_record(record_type, payload):
    """短いNDEF Well Knownレコードを作る。"""
    # TLVの長さを1バイトで表せる範囲に収める。
    if len(payload) > 250:
        raise ValueError("入力されたデータが長すぎます")

    return [0xD1, 0x01, len(payload), record_type] + payload


def write_ndef_data(connection, ndef_record):
    """NDEFレコードをType 2 Tagの4ページ目以降へ書き込む。"""
    ndef_data = [0x03, len(ndef_record)] + ndef_record + [0xFE]

    while len(ndef_data) % 4 != 0:
        ndef_data.append(0x00)

    print("カードへ書き込むデータ:", ndef_data)
    print("書き込むページ数:", len(ndef_data) // 4)

    start_page = 4
    for offset in range(0, len(ndef_data), 4):
        page = start_page + offset // 4
        page_data = ndef_data[offset:offset + 4]
        write_command = [0xFF, 0xD6, 0x00, page, 0x04] + page_data
        _, write_sw1, write_sw2 = connection.transmit(write_command)

        if write_sw1 == 0x90 and write_sw2 == 0x00:
            print(f"ページ{page}を書き込みました")
        else:
            print(f"ページ{page}の書き込みに失敗しました")
            return False

    return True


def main():
    record_type = select_record_type()
    value = input("URLを入力: " if record_type == "2" else "テキストを入力: ")

    try:
        if record_type == "2":
            value = normalize_url(value)
            ndef_record = create_uri_record(value)
            print("書き込むURL:", value)
        else:
            ndef_record = create_text_record(value)
            print("書き込むテキスト:", value)
    except ValueError as error:
        print(error)
        return

    hantei = input("NFCカードに書き込みますか？(y/n): ")
    if hantei.lower() != "y":
        print("書き込みをキャンセルしました")
        return

    reader_list = readers()
    if not reader_list:
        print("カードリーダーが接続されていません")
        return

    reader = reader_list[0]
    print("カードリーダーが接続されました")
    print("機械の名称:", reader)
    print("-----------------------------------------")

    connection = reader.createConnection()
    try:
        connection.connect()
        print("カードに接続しました")
        print("-----------------------------------------")

        if write_ndef_data(connection, ndef_record):
            print("カードへの書き込みが完了しました")
            if record_type == "2":
                print("スマートフォンでカードをタッチしてURLを確認してください")
    except NoCardException:
        print("カードが接続されていません")


if __name__ == "__main__":
    main()
