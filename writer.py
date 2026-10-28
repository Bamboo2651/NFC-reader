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

        if len(payload) > 255:
            print("入力された文字が長すぎます")
            exit()
        ndef_record = [0xD1, 0x01, len(payload), 0x54] + payload
        print("NDEFレコード:", ndef_record)
        

    except NoCardException:
        print("カードが接続されていません")
        exit()