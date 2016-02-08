# -*- coding:utf-8 -*-
from exp_wrapper import template    # パスが通った場所にtemplate.py等を配置しておく


class Example(template.Main):        # templateを継承
    def __init__(self, argv):
        # 親クラスtemplate.Mainのコンストラクタを実行
        super(Example, self).__init__(argv)

    # 基本的な処理内容はexcute(self)に記述する
    def execute(self):
        # コマンドライン引数の情報を取得
        x = self.args.x
        self.logger.info('x = %.2f' % x)
        y = self.args.y
        self.logger.info('y = %.2f' % y)

        # jsonファイルに書き込む情報としてx, yの値を登録
        self.in_params['devidend'] = x
        self.in_params['divisor'] = y

        # 計算
        ans = devide(x, y)
        self.logger.info('x / y = %.2f' % ans)

        # jsonファイルに書き込む情報としてansの値を登録
        self.out_params['devidend/divisor'] = ans

        # 計算結果をファイルに出力
        if self.args.output is not None:
            with open(self.args.output, 'w') as f:
                f.write('divide operation\n')
                f.write('%.2f / %.2f = %.2f' % (x, y, ans))
            # 出力ファイルをself.out_filesに格納
            # これによって, 出力ファイルが, experiment.pyで
            # 作成されたディレクトリに移動される
            self.out_files['result'] = self.args.output

    # 必要に応じて, コマンドライン引数を設定
    def make_parser(self):
        parser = super(Example, self).make_parser()
        # parserの設定
        parser_decsription = """
        Example script for experiment.py
        This script calculate division of x by y.
        """
        parser.description = parser_decsription
        parser.prog = 'example'
        x_help = 'the first argument of divide operation'
        parser.add_argument(
            'x',
            type=float,
            metavar='DIVIDEND',
            help=x_help
        )
        y_help = 'the second argument of divide operation'
        parser.add_argument(
            'y',
            type=float,
            metavar='DIVISOR',
            help=y_help
        )
        output_help = 'output filename'
        parser.add_argument(
            '-o', '--output',
            type=str,
            default=None,
            help=output_help
        )

        return parser


def devide(devidend, devisor):
    return devidend / devisor


# main(argv)は, ほぼ手を加える必要はない
def main(argv):
    obj = Example(argv)     # この部分のみ, クラス名を必要に応じて書き換え
    error = None
    try:
        obj.execute()
    except Exception:
        import traceback
        import sys
        obj.logger.error(traceback.format_exc())
        exc_type = sys.exc_info()[0]
        exc_type_str = exc_type.__name__
        error = exc_type_str
    # ファイルハンドラを閉じる
    from logging import FileHandler
    for handler in obj.logger.handlers:
        if type(handler) is FileHandler:
            handler.close()
    return obj.make_output_json(), error


# experiment.pyを用いずに, 本スクリプトを直接実行する場合は
# こちらが実行される
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
