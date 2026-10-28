from smartcard.System import readers

# while True:
reader_list = readers() # カードリーダーを検索 (デバイスに接続されている機械を探す)
reader = reader_list[0] 
print(reader)