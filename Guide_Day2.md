<div lang="ja">

# プロジェクト研究：P14 コンパイラスイートの作成

## 第2回：2パスアセンブラの構築とラベル付き逆アセンブル

---

## 1. 実験の目的

第1回で作成した簡易トランスレータおよび簡易ディスアセンブラを発展させ、本実験では**ラベル（Symbol）を用いたプログラム記述**と**2パス解析手法**を理解する。

プログラム中のジャンプ先や変数領域を直接ハードコードするのではなく「ラベル」として記述可能にし、さらに後で定義されるラベル（前方参照）の解決も可能な **2パスアセンブラ (`../src/ssc_asm.py`)** を構築する。また、第1回で自身が作成した **逆アセンブラ (`../src/ssc_dis.py`)** に制御フロー解析を追加してラベルを自動復元できるように機能を拡張し、双方向の変換システムを完成させる。

---

## 2. 2パスアセンブラとシンボル解決

### 2.1 前方参照（Forward Reference）の課題

プログラム記述において、まだ定義されていない行番号やラベルへジャンプする処理（前方参照）が存在する。1回の走査（1パス）で機械語に変換しようとすると、ジャンプ先のアドレスが確定していないためアドレス部を空欄にするか複雑な修正（バックパッチ）が必要となる。

### 2.2 2パスアセンブリの仕組み

2パスアセンブラは、ソースコードを2回走査することでこの問題を解決する。

```text
[ソースコード (.sss)]
       │
       ▼
  +----------+
  |  Pass 1  |  ---> 各行のアドレスを計算し、ラベルとアドレスの対応表
  +----------+       (シンボルテーブル) を作成
       │
       ▼
  +----------+
  |  Pass 2  |  ---> シンボルテーブルを参照しながら、ラベルを具体的な
  +----------+       5ビットアドレスに置き換えて機械語コードを生成
       │
       ▼
 [オブジェクトファイル (.sso)]
```

---

## 3. アセンブリ拡張仕様

第2回で作成するアセンブラ（`../src/ssc_asm.py`）では、以下の拡張記法に対応する。

1. **拡張ニーモニック**:
   * 1文字表記（`J`, `A`, `L` 等）に加え、長形式表記（`JUMP`, `ADD`, `LOAD`, `STORE` 等）を解釈する。

2. **ラベル記法**:
   * 行頭に `ラベル名:` を記述することで、その位置のアドレスをシンボルとして登録する（例: `L_start:`）。

3. **疑似命令 (Pseudo-Instructions)**:
   * `lit <数値>`: 指定された整数値をメモリ領域に直接書き込む。
   * `decl <サイズ>`: 変数用領域として指定サイズのメモリ領域を確保する。

---

## 4. 配布ファイルと実験環境

`Day2/` ディレクトリで作業を行うこと。ファイル群およびディレクトリ構造は以下の通りである。

### 4.1 事前準備（ファイルの引き継ぎ）
演習を開始する前に、Day 1 で作成・使用した Python ファイルを `Day2/src/` へコピーすること。

```bash
# Linux / macOS / Git Bash の場合
cp ../Day1/src/*.py src/

# Windows (cmd) の場合
copy ..\Day1\src\*.py src\
```

### 4.2 ディレクトリ構造

```text
Day2/
├── Guide_Day2.md      # 本実験ガイドテキスト
├── src/               # Pythonソースコード
│   ├── ssc_core.py    # (Day1よりコピー) 共通基盤
│   ├── ssc_emu.py     # (Day1よりコピー) エミュレータ
│   ├── ssc_trans.py   # (Day1よりコピー) 参考トランスレータ
│   ├── ssc_asm.py     # 【課題1対象】2パスアセンブラのテンプレート
│   └── ssc_dis.py     # 【課題2対象】Day1で作成したディスアセンブラ（拡張対象）
└── samples/           # 入出力テスト用サンプルプログラム群
    ├── add_label.sss  # ラベル付き加算アセンブリプログラム
    └── loop_label.sss # ラベル付き2倍加算ループアセンブリプログラム
```

---

## 5. タイムスケジュール（目標時間：270分）

| 時間配分 | 内容 |
| --- | --- |
| **30分程度** | 講義：2パスアセンブラの動作原理、到達可能性解析のアルゴリズム解説 |
| **120分程度** | **課題1**: 2パスアセンブラの実装 (`../src/ssc_asm.py`) |
| **120分程度** | **課題2**: 既存の `../src/ssc_dis.py` へのラベル自動復元機能の拡張 |

---

## 6. 実験課題

### 課題1：2パスアセンブラの実装 (`../src/ssc_asm.py`)

`../src/ssc_asm.py` 内の `SSCAssembler` クラスにおける `assemble()` メソッドの **Pass 2** コード生成処理を完成させよ。

#### 実装要件

1. **Pass 1 の理解（提供コード確認）**:
   * ソースコードを走査し、`ラベル:` を検出して現在のアドレス `pc` を `self.symbol_table` に登録する処理を確認すること。
2. **Pass 2 の実装**:
   * `parsed_lines` を順に処理し、各命令に対応する `Word` オブジェクトを生成して `target_mem` に代入する。
   * `lit` 命令 (op_code == 8): `operand` の数値（例: `5` や `0xFF`）を直接 `target_mem[pc].v` に設定。
   * `decl` 命令 (op_code == 9): メモリ領域の確保のみであるためコード生成はスキップ。
   * 通常命令 (0〜7): `operand` がシンボルテーブルに存在する場合は登録アドレスを取得し、存在しない場合は整数値に変換して `Word(op=op_code, addr=addr)` を割り当てる。

#### 実行確認手順

**1. CLI（ターミナル）からの実行確認:**
ターミナルで `Day2/` ディレクトリに移動し、以下のコマンドを実行してラベル付きアセンブリが正しくバイナリコード（`.sso` 形式）に変換されるか確認せよ。

```bash
python src/ssc_asm.py samples/add_label.sss
```

**2. IDE (PyCharm等) からの直接デバッグ実行:**
`../src/ssc_asm.py` の末尾にある `if __name__ == "__main__":` ブロック内のコメントを切り替えることで、組み込みサンプル (`source_text=SAMPLE_PROGRAM`) や指定ファイル (`file="..."`) の動作確認をIDEから直接行えます。

---

### 課題2：既存ディスアセンブラの拡張 (`../src/ssc_dis.py`)

第1回で自身が作成した `../src/ssc_dis.py` に、以下のステップに従ってラベル自動復元機能（`-l` オプション）を追加拡張せよ。

#### 拡張ステップ1: コマンドライン引数（`-l` オプション）の追加

`main()` 関数内の `argparse` 設定およびパラメータ確定部分に、ロングフォーマット出力を指定する `-l` オプションを追加する。

```python
# 1. オプションの追加
parser.add_argument(
    "-l",
    action="store_true",
    help="Output in long assembly format with auto-generated labels",
)

# 2. パラメータの確定（直接引数 > CLI引数）
target_file = file if file is not None else parsed_args.file
use_lflag = lflag if lflag is not None else parsed_args.l
```

確定した `use_lflag` を、`disassembler.disassemble(memory, lflag=use_lflag)` のように `lflag` 引数として渡すよう処理を接続する。

#### 拡張ステップ2: アドレスの役割を表す `Role` の定義

`../src/ssc_dis.py` の冒頭に、各メモリアドレスの役割を保持するための列挙型 `Role` を定義する。

```python
from enum import Enum, auto

class Role(Enum):
    EXECUTABLE = auto()   # 実行可能コード領域
    JUMP_TARGET = auto()  # JUMP先ラベル L00:
    DATA_READ = auto()    # 参照データラベル N00:
    DATA_WRITE = auto()   # 変数書き込みラベル V00:
```

#### 拡張ステップ3: 制御フロー解析関数 `_check()` の追加

`SSCDisassembler` クラスに、プログラムカウンタ `pc=0` から分岐経路を再帰的にたどる `_check()` メソッドを追加する。

```python
def _check(self, memory: list[Word], roles: list[set[Role]], pc: int) -> None:
    while pc < AMAX and Role.EXECUTABLE not in roles[pc]:
        roles[pc].add(Role.EXECUTABLE)
        op = memory[pc].op
        addr = memory[pc].addr

        if op == 0:  # JUMP
            if addr == 0:  # HALT (J/0)
                break
            if addr < AMAX:
                self._check(memory, roles, addr)  # 分岐先を再帰追跡
                roles[addr].add(Role.JUMP_TARGET)
        elif op < 7:  # ADD, SUB, LOAD, STORE, READ, WRITE
            if addr < AMAX:
                roles[addr].add(Role.DATA_READ)
                if op in (4, 5):  # STORE(4), READ(5) は変数書き込み
                    roles[addr].add(Role.DATA_WRITE)
        pc += 1
```

#### 拡張ステップ4: `disassemble()` の出力処理拡張

`disassemble(self, memory: list[Word], lflag: bool = False)` の引数に `lflag` を追加し、以下のように分岐処理を記述する。

1. **`lflag == False` の場合**: 第1回で作成した従来の 1 対 1 簡易出力（`L/5` 等）を行う。
2. **`lflag == True` の場合**:
   * 32ワード分の役割集合リスト `roles = [set() for _ in range(AMAX)]` を用意し、`self._check(memory, roles, 0)` を呼び出す。
   * メモリを走査し、`roles[i]` に含まれる `Role` に応じてラベル（`L00:`, `V00:`, `N00:`）を出力する。
   * 参照アドレス数値を対応するラベル名（例: `LOAD N05` や `JUMP L02`）に置き換えてアセンブリ文字列を整形出力する。

#### 実行確認手順（ラウンドトリップテスト）

自作した `../src/ssc_asm.py` と拡張した `src/ssc_dis.py` を繋ぎ、相互変換テストを行え。

1. **既存サンプル（`../samples/add_label.sss`）を使ったパイプライン実行**:

```bash
python src/ssc_asm.py samples/add_label.sss | python src/ssc_dis.py -l
```

2. **新規テスト用アセンブリ（`samples/sample_label.sss`）を作成して確認する場合**:

`samples/sample_label.sss` を作成：
```text
    load  N_1
    add   N_2
    store V_out
    jump  0
N_1:
    lit 10
N_2:
    lit 20
V_out:
    decl 1
```

パイプライン実行：
```bash
python src/ssc_asm.py samples/sample_label.sss | python src/ssc_dis.py -l
```

3. **確認項目**:
逆アセンブル結果に自動で `L00:`, `V00:`, `N00:` ラベルが付与され、元のプログラム構造が正しく復元されているか確認すること。

---

## 7. 発展課題（任意）

本課題が早期に完了した者は、以下の発展的課題に取り組むこと。

1. **エラーハンドリングの強化**:
`../src/ssc_asm.py` において、存在しないラベルを参照した場合（未定義シンボル）や、メモリ上限（32ワード）を超えた場合に、分かりやすい行番号付きエラーメッセージを表示するよう拡張せよ。
2. **逆アセンブラの最適化表示**:
到達不能領域（`roles[i]` が空の領域）を出力から自動除去するロジックを確認し、静的解析の精度について考察せよ。

---

## 8. レポート課題

実験終了後、以下の項目を含むレポートを作成し次回までに提出すること。

1. 実装した `../src/ssc_asm.py` の Pass 2 コード生成処理のコードと解説。
2. 拡張した `../src/ssc_dis.py` の `_check()` メソッドおよび `-l` オプション処理のコードと解説。
3. 課題1および課題2の実行結果のスクリーンショットまたはログ出力。
4. 考察：アセンブラにおける2パス解析の必要性と、逆アセンブラにおいて静的解析のみで元のラベル名（文字面）を完全復元することの限界・困難さについて述べよ。
