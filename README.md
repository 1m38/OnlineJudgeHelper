# OnlineJudgeHelper

## はじめに
各種オンラインジャッジにて、提出前の入出力チェックを補助するスクリプトです。  
プログラミングの授業などで、課題の採点支援にも利用できます。

## 機能
+ 解答ソースコードのコンパイル
+ 解答コードの実行・入出力チェック・実行時間測定
+ テストケースの管理
+ ソースコードのテンプレート管理

## Usage
### 動作環境
動作にはPython3が必要です。

### 実行方法
#### オンラインジャッジの問題を解く場合
##### 1. setup
問題用のディレクトリを作成し、ソースコード、テストケースファイルを作成します。
``` sh
./oj-helper setup [-c contest_name] -p problem_name [-l language]
```
  カレントディレクトリ以下に`contest_name/problem_name`ディレクトリが作られ、
  その中に`problem_name.language`, `problem_name.sample`ファイルが作成されます。  
  `language`には、使いたい言語のソースコードの拡張子(cpp, pyなど)を指定します。
  指定しなければ、後述する`config.json`内の`dafault_language`の値が使われます。

##### 2. コーディング
`problem_name`ディレクトリに移動し、ソースコード(problem_mane.language)を作成します。
##### 3. テストを追加
``` sh
./oj-helper add-test
```
  問題文に添付されているテストケースの
  入力をコピペする(最後の改行を忘れずに)、Ctrl-Dを押す、出力をコピペする、Ctrl-Dを押すことでテストが登録されます。
  上のコマンドを繰り返し実行することで、複数のテストケースを追加できます。
  誤ったテストケースを追加してしまった場合は、`problem_name.sample`ファイルを直接編集してください。
##### 4. テストを実行
``` sh
./oj-helper test [-l language] [-f filename] [-t timeout]
```
  `filename`を指定しなければ、`problem_name.language`を実行します。
  これ以外のソースコードを実行する場合は指定してください。  
  `timeout`には、問題で指定されている制限時間(秒)を指定します(デフォルト: 2)。
  指定された時間の2倍の時間以内にプログラムが終了しなければ、プログラムの実行を打ち切ります。  

+ 上で使った3つのモード指定(setup, add-test, test)は、それぞれ頭文字を取ったalias(s, a, t)で代用できます。

#### プログラミング課題の採点をする場合
##### 1. setup
問題用のディレクトリを作成し、テストケースファイルを作成します。
``` sh
./oj-helper setup [-c contest_name] -p problem_name [-l language]
```
  ソースコードファイルも作られますが、使用しない場合は削除して構いません。
##### 2. テストを追加
``` sh
./oj-helper add-test
```
##### 3. テストを実行
``` sh
./oj-helper test [-l language] -f filename [-t timeout]
```

## 設定
設定は、`config.json`ファイルに記述します。
+ `default_language`:
  `-l` オプションを指定しなかった場合に使われる言語名を指定します。  
  言語名はソースコードの拡張子としてください。
+ `templates`:
  テンプレートファイルを配置するディレクトリを指定します。
+ `commands`:
  言語ごとに、コンパイルコマンド(`compile_cmd`)、テスト実行コマンド(`test_cmd`)を指定します。  
  インタプリタ言語などコンパイル不要な言語については、`compile_cmd`を省略してください。  
  コマンド中では、ソースコードのファイル名を`{fname}`、コンパイルで生成される実行ファイル名を`{oname}`で指定できます。

## テンプレートファイル
`./oj-helper setup`で作成されるソースコードは、`templates/template.{language}`をコピーすることで作成されています。
このファイルを書き換えたり、新たな言語のテンプレートを追加することでカスタマイズできます。
