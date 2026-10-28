from smartcard.System import readers # カードリーダーを検索するためのモジュール
from smartcard.Exceptions import NoCardException # カードが接続されていない場合の例外処理用

# while True:
reader_list = readers() # カードリーダーを検索 (デバイスに接続されている機械を探す)
if not reader_list:
    print("カードリーダーが接続されていません")
    exit() # カードリーダーが接続されていない場合は終了
reader = reader_list[0] 
print("機械の名称：",reader)
print("-----------------------------------------")

connection = reader.createConnection() # カードと通信するための接続準備
try:
    connection.connect() # RC-S300上のNFCカードへ接続
    print("カードに接続しました")
    print("-----------------------------------------")

    get_uid_command = [0xFF, 0xCA, 0x00, 0x00, 0x00] #UIDを取得するためのコマンド
    data, sw1, sw2 = connection.transmit(get_uid_command) # コマンドを送信してUIDを取得

    if sw1 == 0x90 and sw2 == 0x00: # 正常にUIDが取得できた場合
        box = []
        for byte in data:
            box.append(f"{byte:02X}")
        uid = " ".join(box) # もし "-".join(box)ってやると、"01-02-03"みたいな感じで出力される

        print("10進数UID",data)
        print("16進数UID",uid)
        print("10進数",sw1, sw2)
        print("16進数",f"{sw1:02X}", f"{sw2:02X}")
        print("-----------------------------------------")

        read_command = [0xFF, 0xB0, 0x00, 0x04, 0x10] # カードのデータを読み取るためのコマンド
        card_data, card_sw1, card_sw2 = connection.transmit(read_command) # コマンドを送信してカードのデータを取得

        print("カードのデータ:", card_data)
        print("カード読み取り状態:", f"{card_sw1:02X}", f"{card_sw2:02X}")
        if card_data[0] == 0x03 and card_data[1] == 0x00:
            print("カードにデータはありません")
    else:
        print("UID取得に失敗しました")

except NoCardException:
    print("カードが接続されていません")