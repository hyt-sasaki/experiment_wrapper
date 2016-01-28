# experiment
Wrapper script for experimantal codes.

## 想定している使用方法
gitlog.py，template.pyは  
pythonのパスが通った場所に置く, もしくはシンボリックを張ると便利.  
例)/usr/local/lib/python2.7/dist-packagesにexp_wrapperというフォルダを作成  
exp_wrapper以下のファイル構成  
.  
├── \_\_init\_\_.py  
├── gitlog.py  
└── template.py  

さらにexperiment.pyには  
$> chmod +x experiment.py  
というように, 実行可能ファイルにしておくと使いやすい.  

また, /usr/local/binなど，シェルのパスが通った場所に  
experiment.pyのシンボリックリンクを張ると便利.  
例)experiment.pyが配置されているディレクトリ内で  
$> ln -s \`readlink -f experiment.py\` /usr/loca/bin/experiment

experiment.pyのコマンドラインオプションと  
実行したいpythonファイルのコマンドラインが混同しないように  
experiment.pyのオプションは, prefixが'+'になっている.  

## 実行例
experiment +v +c 'this is an example.' +p example.py -x 1.2 -y 3.1 -o result.txt

## 依存関係
gitlog.pyは, GitPythonを使用しているため,
gitのログを残すためにはGitPythonをインストールする必要がある.

開発ソース
https://github.com/gitpython-developers/GitPython
ドキュメント:
https://gitpython.readthedocs.org/en/stable/
