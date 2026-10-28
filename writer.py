from smartcard.System import readers
from smartcard.Exceptions import NoCardException

text = input("入力：")
print("入力された文字列:", text)
hantei = input("NFCカードに書き込みますか？(y/n): ")
if hantei.lower() == "y":
    reader_list = readers()
    if not reader_list:
        print("カードリーダーが接続されていません")
        exit()
    reader = reader_list[0]
    print("カードリーダーが接続されました")
    print("機械の名称：", reader)
    print("-----------------------------------------")

    connection = reader.createConnection()
    try:
        connection.connect()
        print("カードに接続しました")
        print("-----------------------------------------")
        
        text_bytes = list(text.encode("utf-8"))
        print("UTF-8:", text_bytes)
        language_code = list("ja".encode("ascii"))
        status_byte = len(language_code)
        payload = [status_byte] + language_code + text_bytes
        print("ペイロード:", payload)

        if len(payload) > 250:
            print("入力された文字が長すぎます")
            exit()
        ndef_record = [0xD1, 0x01, len(payload), 0x54] + payload
        print("NDEFレコード:", ndef_record)
        ndef_data = [0x03, len(ndef_record)] + ndef_record + [0xFE]
        print("カードへ書き込むデータ:", ndef_data)
        start_page = 4
        write_succeeded = True

        for offset in range(0, len(ndef_data), 4):
            page = start_page + offset // 4
            page_data = ndef_data[offset:offset + 4]

            write_command = [0xFF, 0xD6, 0x00, page, 0x04] + page_data
            _, write_sw1, write_sw2 = connection.transmit(write_command)

            if write_sw1 == 0x90 and write_sw2 == 0x00:
                print(f"ページ{page}を書き込みました")
            else:
                print(f"ページ{page}の書き込みに失敗しました")
                write_succeeded = False
                break

        if write_succeeded:
            print("カードへの書き込みが完了しました")
        while len(ndef_data) % 4 != 0:
            ndef_data.append(0x00)

        print("4バイト単位へ調整後:", ndef_data)
        print("書き込むページ数:", len(ndef_data) // 4)

    except NoCardException:
        print("カードが接続されていません")
        exit()