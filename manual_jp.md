UdonPie言語 日本語マニュアル
====

コンパイル方法
----

イベント
----
引数なしの例
```py
def _start():
  UnityEngineDebug.Log(SystemObject('start event!!!')))
```

引数ありの例
```py
def _onPlayerJoined(playerApi: VRCSDKBaseVRCPlayerApi):
  UnityEngineDebug.Log(SystemObject(playerApi))
```

Udon Extern関数呼び出し
----
### スタティック関数
`[Udonの型名（モジュール）].[メソッド](引数1, ...)`

### コンストラクタ
`[Udonの型名（モジュール）].ctor(引数1, ...)`

### インスタンス関数
`[インスタンス変数].[メソッド](引数1, ...)`


リテラル
----
### 整数値


### 浮動小数（float）


### 文字列


変数
----

### 宣言方法

### global変数


### 型

配列
---

数値演算
----

論理演算
----

制御構文
----

### 代入文

### if文

### while文

### return文

### Import文（未実装）

キャスト
----

関数
----

```
def func1(x_1: SystemInt32, y_1: SystemInt32) -> SystemInt32:
  return 2 * x_1 + y_1
```


注意点
----

予約語
----
