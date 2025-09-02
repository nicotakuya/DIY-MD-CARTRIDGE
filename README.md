# DIY MD CARTRIDGE

## 概要
メガドライブ用のフラッシュROMのカートリッジ基板です。容量は8Mbit。
動作無保証。

## ファイルの説明
・MD_CART.COMP : プリント基板データ。CADLUS X用。

・MD_WR.COMP : プリント基板データ。CADLUS X用。

・wr_md.py : フラッシュROM書き込みプログラム。Raspberry Pi+Python用。

・md.prg : フラッシュROM書き込みプログラム。Raspberry Pi+Pi STARTER用。

## 部品リスト
### カートリッジ基板

・4Mbit フラッシュメモリ SST39SF040-70-4C-PHE

・3mm LED

・4.7k ohm 抵抗

・積層セラミックコンデンサまたは電解コンデンサ

### フラッシュメモリライター

・I/Oエキスパンダ  MCP23S17-E/SP
http://akizukidenshi.com/catalog/g/gI-10644/

・ロジックIC 74HC32AP
http://akizukidenshi.com/catalog/g/gI-12877/

・ピンソケット(28~40ピン推奨)

・カードエッジコネクタ64ピン

・LED 3mm

・抵抗

・小信号ダイオード

・低損失5V三端子レギュレータ 48M05
