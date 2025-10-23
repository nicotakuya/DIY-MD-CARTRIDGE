# DIY MD CARTRIDGE

## 概要
メガドライブ用のフラッシュROMのカートリッジ基板です。容量は8Mbit。
動作無保証。
<img width="769" height="453" alt="Image" src="https://github.com/user-attachments/assets/1d0aa57c-2429-486c-999d-d74b166e0c87" />

## ファイルの説明
・MD_CART.COMP : カートリッジ基板のプリント基板データ。CADLUS X用。

・MD_WR.COMP : フラッシュメモリライターのプリント基板データ。CADLUS X用。

・wr_md.py : フラッシュROM書き込みプログラム。Raspberry Pi+Python用。

・md.prg : フラッシュROM書き込みプログラム。Raspberry Pi+Pi STARTER用。

・md_cart_schematics.png : 回路図。

・md_wr_schematics.png : 回路図。

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

・2.54mmピッチ 2x20pin ピンソケット

・カードエッジコネクタ64ピン

・LED 3mm

・抵抗

・小信号ダイオード

・低損失5V三端子レギュレータ 48M05
