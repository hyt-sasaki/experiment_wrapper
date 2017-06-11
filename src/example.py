# -*- coding:utf-8 -*-
## @package example
#
#  実験用スクリプトの具体例が記述されているパッケージ
from exp_wrapper import template
from exp_wrapper.decorator import arg_decorator
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter


## 実験用スクリプトのメインとなるクラス
#
#  実験用スクリプトのメインとなるクラスで, template.Mainを継承する.
class Example(template.Main):        # templateを継承
    ## コンストラクタ
    #  @param self オブジェクト自身に対するポインタ
    #  @param argv コマンドライン引数を保持するリスト
    def __init__(self, argv):
        self.make_calc_parser()
        self.make_io_parser()
        # 親クラスtemplate.Mainのコンストラクタを実行
        super(Example, self).__init__(argv)

    ## メイン処理を行うメソッド
    #
    # 実験用スクリプトのメイン処理を行うメソッド.
    # 基本的な処理内容は本メソッドに記述する.
    def execute(self):
        # コマンドライン引数の情報を取得
        x = self.args.calc.x
        self.logger.debug('x = %.2f' % x)
        y = self.args.calc.y
        self.logger.debug('y = %.2f' % y)

        # jsonファイルに書き込む情報としてx, yの値を登録
        self.in_params['devidend'] = x
        self.in_params['divisor'] = y

        # 計算
        ans = devide(x, y)
        self.logger.info('x / y = %.2f' % ans)

        # jsonファイルに書き込む情報としてansの値を登録
        self.out_params['devidend/divisor'] = ans

        # 計算結果をファイルに出力
        if self.args.io.output is not None:
            with open(self.args.io.output, 'w') as f:
                f.write('divide operation\n')
                f.write('%.2f / %.2f = %.2f' % (x, y, ans))
            # 出力ファイルをself.out_filesに格納
            # これによって, 出力ファイルが, experiment.pyで
            # 作成されたディレクトリに移動される
            self.out_files['result'] = self.args.io.output

    ## コマンドライン引数のパーサを生成するメソッド
    #
    #  コマンドライン引数のパーサを生成するメソッドで,
    #  必要に応じたコマンドライン引数を設定する.
    #  @param self オブジェクト自身に対するポインタ
    #  @return parser パーサオブジェクト
    def make_parser(self):
        parser = super(Example, self).make_parser()
        # parserの設定
        parser_decsription = """
        Example script for experiment.py.
        This script calculate division.
        """
        parser.description = parser_decsription
        parser.prog = 'example'
        parser.formatter_class = ArgumentDefaultsHelpFormatter

        return parser

    @arg_decorator('calc')
    def make_calc_parser(self):
        parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        g = parser.add_argument_group('calc arguments')
        x_help = 'the first argument of divide operation'
        g.add_argument(
            'x',
            type=float,
            metavar='DIVIDEND',
            help=x_help
        )
        y_help = 'the second argument of divide operation'
        g.add_argument(
            'y',
            type=float,
            metavar='DIVISOR',
            help=y_help
        )

        return parser

    @arg_decorator('io')
    def make_io_parser(self):
        parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        g = parser.add_argument_group('I/O settings')
        output_help = 'output filename'
        g.add_argument(
            '-o', '--output',
            type=str,
            default=None,
            help=output_help
        )

        return parser


## 割り算を行う関数
#  @param devidend 被除数
#  @param devisor 除数
def devide(devidend, devisor):
    return devidend / devisor


# experiment.pyを用いずに, 本スクリプトを直接実行する場合は
# こちらが実行される
if __name__ == '__main__':
    import sys
    obj = Example(sys.argv[1:])
    template.main(obj)
