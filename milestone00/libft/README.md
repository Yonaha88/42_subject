*This project has been created as part of the 42 curriculum by kyonaha.*

# libft

## Description
C標準ライブラリの関数を自分で再実装したライブラリ。
今後の42の課題で外部ライブラリとして使用するために作成した。
文字列・メモリ操作・文字判定・出力・単方向リストなど43関数で構成される。

## Instructions
ライブラリのビルド：
```
make
```
自分のプロジェクトで使う場合は `libft.a` と `libft.h` を同じディレクトリに置き、コンパイル時にリンクする：
```
cc main.c libft.a
```

## Resources

### ft_strmapi
関数ポインタの説明
https://qiita.com/lightfel/items/04d293ccf2b2184ddc26

### ft_lstnew
単方向リストについて
https://note.com/kazushinakamura/n/n64a0ba7d3d09
構造体の宣言、使い方について
https://www.sejuku.net/blog/24473

### AIをどう使った？
調べてわからない、地に足つかないときに解説。
関数作成後の最終チェック。
makefileの解説。



## Feature list
関数の説明。

### ft_isalpha
英字かどうかの判定を行う。
引数がintなのはEOF（ファイルの終わり）が-1という値を示し、unsigned charだと255との区別がつかないから。
戻り値は課題pdfより、正しければ１、そうでなければ０。

### ft_isdigit
数字かどうかの判定を行う。

### ft_isalnum
英字もしくは数字であるかどうかの判定を行う。

### ft_isascii
ASCII文字かどうかの判定を行う。
ASCIIは０〜１２７。

### ft_isprint
表示可能文字かどうかの判定を行う。
表示可能文字は３２〜１２６

### ft_strlen
文字列の長さを返す。
ヌル文字は含まない。
strがNULLのとき、未定義動作。

### ft_memset
srcからnumバイト分だけchrで埋める。
もしsrcが確保したもの以上にnumがあったら、未定義動作。
chrがint型なのは、昔のｃで関数引数が自動的にintに昇格するという仕様があったから。
chrがint型のため、関数内部でunsigned charに型変換している

### ft_bzero
srcからnumバイト分だけ0で埋める。
戻り値がないのは、ゼロ埋めは必ず成功するという前提があったため。

### ft_memcpy
srcからdestへ、numバイト分コピーする。

### ft_memmove
srcからdestへ、numバイト分コピーする。
ft_memcpyと異なり、メモリ領域が重なっていてもコピーができる。
実装の方法として、一時的にsrc,destを移し替えるのではなく、ポインタの位置によってコピーする順番を変えた。

### ft_strlcpy
srcからdestへ、size-1文字コピーする。
size字目に終端文字を入れる。
戻り値は、srcの文字数。

### ft_strlcat
destの終端文字から、全体の文字がsize-1文字になるまでsrcを昇順に付け加える。
戻り値はdest+srcの文字数。
destの文字数がsize以上の場合何もしない。このときの戻り値も通常と同じ。

### ft_toupper
小文字を大文字にして返す。

### ft_tolower
大文字を小文字にして返す。

### ft_strchr
文字列strの中で初めて出てきた文字chrのポインタを返す。
strの中にchrがなければNULLを返す。

### ft_strrchr
文字列strの中で最後に出てきた文字chrのポインタを返す。

### ft_strncmp
2つの文字列を最大ｎバイトまで比較する。
文字が違ったら、asciiの差を返す。
終端文字が来たら、その時点で比較終了。

### ft_memchr
memの中にchrがあったら抜き出す。
(unsigned char *)src[idx]ではidxの型がわからないため
((unsigned char *)src)[idx]とした。

### ft_memcmp
src1とsrc2の先頭からnumバイト比較する。
はじめに異なるバイトの差を返す。
すべて一致した場合０を返す。

### ft_strnstr
bigの先頭からlen文字の間に文字列littleがないかを探す。
あれば、その先頭ポインタを返す。
なければ、NULLを返す。

### ft_atoi
nbrptrを数字にして返す。
数字が始まるまでの空白文字は無視する。
数字の前の符号はひとつだけ参考にする。
オーバーフロー時は未定義動作。

### ft_calloc
nmemb * size の数だけメモリを確保し、0で初期化する。
どちらかが０のときはfreeできるポインタを返す。
nmemb * size が size_t よりも大きい値になったらNULLを返す。

### ft_strdup
srcの文字列を複製し、新たに確保したメモリにコピーして返す。
返されたポインタはfreeする必要がある。
メモリ確保に失敗した場合はNULLを返す。

### ft_substr
文字列sのstart番目から最大len文字の部分文字列を新たに確保したメモリにコピーして返す。
startがsの長さ以上の場合は空文字列を返す。

### ft_strjoin
src1とsrc2が結合した文字列を返す。

### ft_strtrim
文字列srcの先頭と末尾から、setに含まれる文字をすべて除去した文字列を新たに確保したメモリにコピーして返す。
setに含まれない文字が現れた時点でトリムを停止する。

### ft_split
cを区切り文字として文字列srcを分割して、各文字列をmallocして確保した文字列の配列を返す。
mallocに失敗したら、いままで確保したメモリをfreeで開放してから返す。
配列の最後はNULLである。

### ft_itoa
整数を受け取り、文字列にして返す。
負の数にも対応している。

### ft_strmapi
文字列sの各文字に対して、インデックスと文字を引数として関数fを適用し、結果を新たに確保したメモリにコピーして返す。
メモリ確保に失敗した場合はNULLを返す。

### ft_striteri
文字列sの各文字に対して、インデックスと文字へのポインタを引数として関数fを適用する。
ft_strmapiと異なり、文字列を直接変更する。戻り値はない。

### ft_putchar_fd
文字cを指定されたファイルディスクリプタに出力する

### ft_putstr_fd
文字列sを指定されたファイルディスクリプタに出力。

### ft_putendl_fd
ft_putstr_fdと同じ働きをした後、改行を出力する。

### ft_putnbr_fd
整数ｎを指定されたファイルディスクリプタに出力する。

### ft_lstnew
新しいリストノードを作成し、contentにcontentを設定してnextをNULLにして返す。
mallocに失敗した場合はNULLを返す。

### ft_lstadd_front
リストの先頭に新しいノードnewを追加する。

### ft_lstsize
リストのノード数を返す。

### ft_lstlast
リストの最後のノードを返す。

### ft_lstadd_back
リストの末尾に新しいノードnewを追加する。

### ft_lstdelone
ノードのcontentに関数delを適用してからfreeする。

### ft_lstclear
リストの全ノードのcontentに関数delを適用し、freeして、ポインタをNULLにする。

### ft_lstiter
リストの各ノードのcontentに関数fを適用する。
fがNULLの場合は何もしない。

### ft_lstmap
リストlstの各ノードのcontentに関数fを適用した結果で新しいリストを作成して返す。
mallocに失敗した場合は、それまでに確保したリストをdelを使ってfreeしてからNULLを返す。
lst・f・delのいずれかがNULLの場合はNULLを返す。

