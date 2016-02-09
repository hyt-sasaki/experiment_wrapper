# experiment
Wrapper script for experimantal codes.

## 概要
実験用のpythonコードを引数として, 様々な処理を行う.  
主な機能としては,  
- 実験結果保存用のディレクトリを作成
- 実験時の各種パラメータをjsonファイルに出力
- gitを用いている場合, 実行時のコミットIDをファイルに保存
- 実行時に出力内容をログファイルに保存

などがある.

## インストール方法
$> git clone https://github.com/hyt-sasaki/experiment_wrapper.git  
$> cd experiment_wrapper  
$> python setup.py install  
    もしくは  
$> sudo python setup.py install  

## 実行例
上記の続きで(experiment_wrapperディレクトリにいる状態で)  
$> experiment +v 10 +c 'this is an example.' src/example.py Example -o result.txt 10.0 2.1  
詳しくは  
$> experiment +h  
のヘルプを参照.

## 使用方法
experimentスクリプトで読み込むpythonファイルに  
1. exp_wrapper.template.Mainを継承したクラスを定義する.  
2. メソッドexcute(self)に行いたい処理を記述する.  
3. コマンドライン引数をmake_parser(self)で定義する.

基本的には, example.pyを参考に.  

exp_wrapper.template.Mainには次のメンバ変数が用意されている.  
1. in_params: 入力パラメータを保存する辞書. 初期状態ではコマンドライン引数の値が保存される.  
2. out_params: 出力パラメータを保存する辞書.  
3. in_symlinks: シンボリックリンクを張りたい入力ファイル名を保存する辞書.  
4. out_symlinks: シンボリックリンクを張りたい出力ファイル名を保存する辞書.  
5. out_files: 出力ファイル名を保存する辞書.  

これらのメンバ変数の内容はjsonファイルに出力される.  
また, in_symlinksおよびout_symlinksに保存されたファイルに対しては, 出力ディレクトリに対象ファイルのリンクが張られる.  
out_filesに保存されたファイルに関しては, 出力ディレクトリに自動的に移動される.  
## 依存関係
gitlog.pyはGitPythonを使用しているため,
インストールがされていない場合はsetup.pyで自動にインストールを行う.

開発ソース
https://github.com/gitpython-developers/GitPython  
ドキュメント:
https://gitpython.readthedocs.org/en/stable/
