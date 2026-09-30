import sys
from ssc_core import AMAX, Word


class SSCAssembler:
    """【第2回 課題1】トランスレータ (ssc_trans) を拡張し、

    2パスアセンブラを完成させよ。
    """

    # 命令および疑似命令のニーモニックマップ
    OP_MAP = {
        "J": 0, "JMP": 0, "JUMP": 0,
        "A": 1, "ADD": 1,
        "B": 2, "SUB": 2,
        "L": 3, "LOAD": 3,
        "T": 4, "STORE": 4,
        "R": 5, "READ": 5,
        "W": 6, "WRITE": 6,
        "S": 7, "SHIFT": 7,
        "D": 8, "LIT": 8, "LITERAL": 8,
        "DECL": 9, "STORAGE": 9,
    }

    def __init__(self):
        self.symbol_table: dict[str, int] = {}

    def assemble(
        self, source_text: str, memory: list[Word] | None = None
    ) -> list[Word]:
        """アセンブリ言語ソースを解析し、指定されたメモリ配列に結果を上書きして返す"""
        if memory is None:
            memory = []

        target_mem = (
            [w.copy() for w in memory] + [Word(0) for _ in range(AMAX)]
        )[:AMAX]

        lines = source_text.splitlines()
        self.symbol_table.clear()

        parsed_lines = []
        pc = 0

        # -------------------------------------------------------------
        # TODO: Pass 1 - ラベル解析とアドレス計算
        #  各行から "ラベル:" を検出し、現在のアドレス (pc) を self.symbol_table に登録せよ。
        #  DECL 命令(op_code == 9) の場合は、指定されたサイズ分 pc を進めること。
        # -------------------------------------------------------------
        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.split(";")[0].split("/")[0].strip()
            if not line:
                continue

            label = None
            if ":" in line:
                label_part, line = line.split(":", 1)
                label = label_part.strip()
                line = line.strip()

            # TODO: ラベルが存在する場合、self.symbol_table[label] = pc で登録せよ
            if label:
                self.symbol_table[label] = pc

            if not line:
                continue

            tokens = line.split(maxsplit=1)
            opcode_str = tokens[0].upper()
            opaddr_str = tokens[1].strip() if len(tokens) > 1 else ""

            if opcode_str not in self.OP_MAP:
                raise SyntaxError(
                    f"Line {line_num}: Unknown mnemonic '{opcode_str}'"
                )

            op_code = self.OP_MAP[opcode_str]

            # アドレスの加算幅 (DECL の場合は引数分の領域を確保)
            inc = 1
            if op_code == 9:  # DECL
                inc = int(opaddr_str, 0) if opaddr_str else 1

            parsed_lines.append(
                {
                    "pc": pc,
                    "op": op_code,
                    "operand": opaddr_str,
                    "raw": raw_line,
                }
            )
            pc += inc

        if pc > AMAX:
            raise MemoryError(
                f"Program size ({pc} words) exceeds max memory limit ({AMAX} words)."
            )

        # -------------------------------------------------------------
        # TODO: Pass 2 - 機械語コード生成
        #  parsed_lines を走査し、各命令に対応する Word オブジェクトを生成して
        #  target_mem に格納せよ。
        #  - op_code == 8 (D / LIT) : operand_str の定数値を直接 target_mem[pc].v に代入
        #  - op_code == 9 (DECL)    : メモリ確保のみのためスキップ
        #  - 通常命令 (0-7)         : operand_str がシンボルテーブルにあればそのアドレスを使用し、
        #                             Word(op=op_code, addr=addr) を生成して代入
        # -------------------------------------------------------------
        raise NotImplementedError("SSCAssembler.assemble() の Pass 2 を実装してください。")

        return target_mem


def main(
    args_list: list[str] | None = None,
    file: str | None = None,
    source_text: str | None = None,
):
    import argparse

    parser = argparse.ArgumentParser(
        prog="ssc_asm", description="SSC Assembler (2-Pass Assembler)"
    )
    parser.add_argument(
        "file", nargs="?", type=str, default=None, help="Input .sss file"
    )

    parsed_args = parser.parse_args(args_list)
    target_file = file if file is not None else parsed_args.file

    if source_text is None:
        if target_file:
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    source_text = f.read()
            except OSError as e:
                sys.stderr.write(f"ssc_asm: {e}\n")
                sys.exit(2)
        else:
            source_text = sys.stdin.read()

    assembler = SSCAssembler()
    try:
        assembled_mem = assembler.assemble(source_text)
    except (SyntaxError, MemoryError, NameError, NotImplementedError) as e:
        sys.stderr.write(f"ssc_asm error: {e}\n")
        sys.exit(1)

    for i, w in enumerate(assembled_mem):
        print(f"{i:02d}: {w.to_bin()}")


if __name__ == "__main__":
    main()
