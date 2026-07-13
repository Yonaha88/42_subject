*This project has been created as part of the 42 curriculum by kyonaha.*

# ft_printf

## Description

C標準ライブラリ関数 `printf()` の再実装。
`libftprintf.a` としてコンパイルされ、以下の変換指定子に対応している。
%c, %s, %p, %d, %i, %u, %x, %X, %%

## Instructions

make で libftprintf.a を作成。

cc your_file.c libftprintf.a でコンパイル。

/a.out で実行。

## Resources

- man 3 printf — printf の仕様
- man 3 stdarg — va_start, va_arg, va_end, va_copy
- 可変長引数関数に関する記事 https://qiita.com/keitean/items/fd2be6710efe681cc516
- Claude — 可変長引数の仕組み・バッファ管理・例外処理の挙動などの概念理解

## Algorithms

### フォーマット文字列を調べる

フォーマット文字列を1文字ずつ走査する。
% を発見したら次の文字で変換指定子を判定し、対応する出力関数に処理させる。

### 整数の文字列変換 (%d, %i, %u)

10で繰り返し割り算しながら余りを収集して文字列に変換。
INT_MIN は絶対値を取るとオーバーフローするため、long 型にキャストして処理。

### 16進数変換 (%x, %X, %p)

再帰的に実装。16で割った商を再帰し、余りに対応する文字を出力。
%p も同じ関数を再利用し、ポインタを unsigned long long にキャストして渡す。

### 例外処理

- %s に NULL が渡された場合は "(null)" を出力
- %p に NULL が渡された場合は "(nil)" を出力
- %p は16進数アドレスの前に "0x" を付ける。"0x"は16進数であると表すもの。

