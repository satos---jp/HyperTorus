# 枕
二次元言語(Befunge, Fish, Rail, Hexagony,Piet 等)はesolangだが書きにくいわけではない。
コードがn次元ならより書きづらい言語になるのでは？
HyperTorusは、コードとメモリがn次元トーラスでできている言語です。

# 実行
`python3 interpreter.py sourcecode`
## デバッグオプション
- -n [number]
  実行の number ステップ毎に内部状態をダンプする
- -b [str]
  str の d 文字目が `#` なら、プログラムの座標 d を実行するたびに内部状態をダンプする
(-n と -b を同時に指定することもできます)

# 仕様
## プログラムの記述
プログラムは1行で入力される。
たとえば、
```
abcdefgh
```
というプログラムは、

```
     g------h
    /|     /|
   / |    / |
  e--+---f  |
  |  c---+--d   
  | /    | /   
  |/     |/     
  a------b      
  ```

という3次元トーラス上に配置される。

一般的に、長さ 2^n 以上 2^(n+1) 未満 のプログラムはn次元トーラスを表現する。

以降ではプログラムの各座標を2進数で表現する。たとえば座標(0,0,0) は2進数000、
座標 (0,1,1) は二進数 110 といった具合である。leading zero は適宜省略する。

座標 k にはプログラムの k 文字目が入る。

## 命令ポインタ

命令ポインタが1つ、いずれかの座標上に、座標軸と並行な向きを向いて存在している。
実行の1ステップごとに、命令ポインタは現在の向きの方向に移動し、移動先の座標にある命令を実行する。

命令ポインタの状態は、命令ポインタの座標と向きによって表現される。
たとえば上の図において、(010,+4) は b に存在して f のほうを向いている命令ポインタの状態を表現している。

初期状態では、メモリポインタの状態は (0,+1) である。

例えば上の例だと、初期状態から命令が a b a b a b ... と実行される。

## メモリセル
メモリは、大きさ2^Z(このZは整数の集合)のトーラスでできており、各辺上に(多倍長)整数値を保存する。(発想元はhexagonyのメモリですね)
以降では各メモリ位置を、ちょうど一つの桁にxを含んだ01数字列で表示する。また桁数が分かるようにするため、0桁目の右に'.'をつけることにする。
たとえば、 10x0.01 は、 3桁目と-2桁目が1、1桁目がxで、そのほかの桁が0であるようなメモリ位置を表現している。

メモリポインタがちょうど1つ、いずれかの辺上に向きつきで存在する。メモリポインタの位置は、ちょうど一つの桁に+もしくは-を含んだ01数字列で表示する。
たとえば、 10+0.01 は、メモリ 10x0.01 にあって、 1000.01 から 1010.01 方向を向いて存在しているメモリポインタとし、 10-0.01 は、メモリ10x0.01に存在する10+0.011と逆向きのメモリポインタとする。

単項演算([0-9a-f]によるセットや','によるread charや'.'によるwrite charなど)を行うと、現在のメモリポインタの指しているメモリについて演算が行われる。

二項演算(+-*/による加減乗除など)を行うと、現在のメモリポインタに対して左側のメモリと右側のメモリの演算結果が現在のメモリポインタの指しているメモリに入る。たとえば、メモリポインタが 10+0.01 の場合に減算-を行うと、 10x0.01 に 1x00.01 から 100x.01 を引いた結果が格納されることになる。

初期状態でのメモリポインタの状態は +.0 であり、すべてのメモリは値0で初期化されている。

また、レジスタを1つ持っている。

# 命令一覧 
## 命令ポインタ操作命令 
| char | operation |
|---|---|
| &#124; | 命令ポインタの向き、つまり向きの符号を反転させる。|
| &lt; |命令ポインタの向きを左に向ける(たとえばプログラムが4次元トーラスの場合、向きは +1→+2→+4→+8→+1 もしくは -1→-8→-4→-2→-1 と変化する)|
| &gt; |命令ポインタの向きを右に向ける(たとえばプログラムが4次元トーラスの場合、向きは  +1→+8→+4→+2→+1 もしくは -1→-2→-4→-8→-1 と変化する)|
| ? | 現在のメモリの値が0なら &lt; と、そうでないなら &gt; と同じ動きをする |
| j | 「現在のメモリの値をプログラムサイズで割ったあまりの位置」に(命令ポインタの向きはそのままで)ジャンプする |
| . | 何もしない(NOP) |
| @ | プログラムの実行を終了ずる |

## メモリ系命令
### メモリポインタ操作命令
| char | operation |
|---|---|
| $ | メモリポインタの向きを反転させる(+-が反転する) |
| { | メモリポインタを左に向ける (100+.01 は 10+0.01 に、 100-.01 は 10-1.01 になる) |
| } | メモリポインタを右に向ける (100+.01 は 1000.+1 に、 100-.01 は 1001.-1 になる) |

### 値のセット 
| char | operation |
|---|---|
| [0-9a-f] | メモリポインタの指すメモリの値をx(16進で)にする |
| & | メモリの値をレジスタに出し入れする。&の実行ごとに、命令の意味が「レジスタの値をメモリの値にする」<->「メモリの値をレジスタの値にする」 となる。 |
### 二項演算命令 

| char | operation |
|---|---|
| + | 加算 |
| - | 減算 |
| * | 乗算 |
| / | 除算 (0割りはエラー) |
| % | 剰余 (0割りはエラー) |
| = | a=bなら1,そうでないなら0|
| ( | a<bなら1,そうでないなら0|
| ) | a>bなら1,そうでないなら0|
### IO命令 
| char | operation |
|---|---|
| r | メモリポインタの指すメモリの値を読み込んだ文字のアスキーコード値にする(EOFなら-1) |
| w | メモリポインタの指すメモリの値を256で割ったあまりの文字を出力する |
| i | メモリポインタの指すメモリの値を(区切り文字まで)読み込んだ十進数値にする |
| o | メモリポインタの指すメモリの値を十進数で出力する |


# コード例 
### cat 
```
r<.w.{j<)<@?...<
```

# 募集
いいかんじのビジュアライザ
