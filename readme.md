# dsCheck
金沢工業大学 電子計算機研究会用の出席管理システム

:warning: pip による `pygame nfcpy` のライブラリインストールが必要です。
```
python -m pip install pygame nfcpy
pip install pygame nfcpy
```

## ファイル
+ `list.csv` に名簿 `{学籍番号,名前}` を予め登録してください。
+ `checked.csv` に出席が確認できた学生が随時登録されます。
+ `external.csv` に出席確認が任意な学生や事前連絡があった学生を登録しておくと無断欠席の集計対象外とすることが出来ます。

## 使用方法
1. `start.bat` を起動するか `NFC_Record.py` を実行します。
2. 各々に学生証をかざして貰います。
3. ウィンドウを閉じると出席を締め切り、無断欠席者の集計が `absent_XXXX.log` (`XXXX`は年月) に記録されます。
4. 間違えてウィンドウを閉じて終了した後でも、再度 1. からやり直すことで出席確認を再開することが出来ます。


***
> nakanolab による [NFC対応学生証による出席確認ツール](https://github.com/nakanolab/nfc-attendance) のソースを利用しています。