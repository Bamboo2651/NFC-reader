# NFC Reader

Sony RC-S300を使って、NFCカードの読み取りと書き込みを試すPythonプロジェクトです。

## ファイルの説明

### `main.py`

NFCカードの読み取り用ファイルです。

- RC-S300とNFCカードの接続を待つ
- カードのUIDを読み取る
- NDEF形式で保存されたテキストを表示する
- カードを離すと次の読み取りを待つ
- `Ctrl + C`で終了する


### `writer.py`

NFCカードへの書き込み用ファイルです。

- テキストまたはWebサイトのURLを入力する
- 入力内容をNDEFのTextレコードまたはURIレコードに変換する
- RC-S300にかざしたNFCカードへデータを書き込む
- URIレコードを書き込んだカードをスマートフォンでタッチすると、Webサイトを開ける


## 事前準備

### RC-S300のドライバー

RC-S300をPCで認識させるため、[ソニーの公式サイト](https://www.sony.co.jp/Products/felica/consumer/?j-short=pasori)から必要なソフトウェアをインストールします。

### Pythonライブラリー

```powershell
python -m pip install pyscard==2.3.2
```

## 注意

`writer.py`を実行すると、カードに保存されているデータが書き換えられます。
