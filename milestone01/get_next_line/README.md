*This project has been created as part of the 42 curriculum by kyonaha.*

## Description

ファイルディスクリプタから1行ずつ読み込んで返す関数を実装する課題。静的変数について学ぶことが目的。

## Instructions

コンパイル例（BUFFER_SIZEは任意の値を指定する）:

```
cc -Wall -Wextra -Werror -D BUFFER_SIZE=42 get_next_line.c get_next_line_utils.c main.c
```

ボーナスをコンパイルする場合:

```
cc -Wall -Wextra -Werror -D BUFFER_SIZE=42 get_next_line_bonus.c get_next_line_utils_bonus.c main.c
```

実行方法:

```
./a.out
```

## Algorithm

get_next_lineを呼び出すたびに、BUFFER_SIZE バイトずつ fd から読み込み、remainder[fd] という静的配列に蓄積する。`\n` が見つかった時点で読み込みを止め、その行を返す。`\n` より後ろの余りは remainder[fd] に残しておき、次の呼び出しで先頭から使う。

fdごとに remainder の要素が独立しているため、複数の fd を同時に扱える。静的変数は remainder[OPEN_MAX] の1つのみである。

## Resources

- [C言語リファレンス: read()](https://man7.org/linux/man-pages/man2/read.2.html)
- [C言語リファレンス: static変数](https://en.cppreference.com/w/c/language/storage_duration)

AIの使用について: Claudeを使用し、概念理解・バグの指摘・コードのレビューを行った。
