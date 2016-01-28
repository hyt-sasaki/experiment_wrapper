# -*- coding:utf-8 -*-
import argparse
import logging
from exp_wrapper.template import template    # パスが通った場所にtemplate.py等を配置しておく


class Example(template):        # templateを継承
    def __init__(self, argv):
        # parserの取得
        # make_parser()は使用方法に従って実装
        parser = make_parser()
        # 親クラスtemplateのコンストラクタを実行
        super(Example, self).__init__(parser, argv)

    # 基本的な処理内容はexcute(self)に記述する
    def execute(self):
        # logging.info(msg)の情報を出力するかどうか
        # self.in_paramsにはmake_parserで取得したコマンドライン引数が格納される
        if self.in_params['verbose']:
            logging.basicConfig(level=logging.INFO)

        # コマンドライン引数の情報を取得
        x = self.args.x
        logging.info('x = %.2f' % x)
        y = self.args.y
        logging.info('y = %.2f' % y)

        # jsonファイルに書き込む情報としてx, yの値を登録
        self.in_params['x'] = x
        self.in_params['y'] = y

        # 計算
        ans = x + y
        logging.info('x + y = %.2f' % ans)

        # jsonファイルに書き込む情報としてansの値を登録
        self.out_params['x+y'] = ans

        # 計算結果をファイルに出力
        if self.args.output is not None:
            with open(self.args.output, 'w') as f:
                f.write('add operation\n')
                f.write('%.2f + %.2f = %.2f' % (x, y, ans))
            # 出力ファイルをself.out_filesに格納
            # これによって, 出力ファイルが, experiment.pyで
            # 作成されたディレクトリに移動される
            self.out_files['result'] = self.args.output


# main(argv)は, ほぼ手を加える必要はない
def main(argv):
    obj = Example(argv)     # この部分のみ, クラス名を必要に応じて書き換え
    error = None
    try:
        obj.execute()
    except Exception, e:
        print e.message
        error = e.message.__str__()
    return obj.make_output_json(), error


# 必要に応じて, コマンドライン引数を設定
def make_parser():
    # parserの設定
    parser_decsription = """
    Example script for experiment.py
    This script calculate sum of x and y.
    """
    parser = argparse.ArgumentParser(
        description=parser_decsription,
        prog='example'
    )
    x_help = 'the first argument of add operation'
    parser.add_argument(
        '-x',
        type=float,
        help=x_help
    )
    y_help = 'the second argument of add operation'
    parser.add_argument(
        '-y',
        type=float,
        help=y_help
    )
    output_help = 'output filename'
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help=output_help
    )
    verbose_help = 'show logging info'
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help=verbose_help
    )

    return parser

# experiment.pyを用いずに, 本スクリプトを直接実行する場合は
# こちらが実行される
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
