# -*- coding:utf-8 -*-
## @package template
#
#  実験用スクリプトのテンプレートが定義されているパッケージ
import json
import argparse
from logging import getLogger
from logging import StreamHandler, FileHandler
from logging import INFO, DEBUG
from logging import Formatter
from inspect import currentframe
from os.path import splitext, split


## スクリプトのメインとなるテンプレートクラス
#
#  実験用スクリプトのメインとなるテンプレートクラス.@n
#  このMainクラスは継承して利用することを想定している.@n
#  継承先のクラスでは, excute()とmake_parser()をオーバーライドする.@n
class Main(object):
    ## コンストラクタ
    #  @param self オブジェクト自身に対するポインタ
    #  @param argv コマンドライン引数を保持するリスト
    def __init__(self, argv, parents_dict={}):
        ## @var args
        #  コマンドライン引数のリスト
        self.args = None
        self.parse_args(argv, parents_dict)
        ## @var in_params
        #  入力パラメータの辞書(コマンドライン引数で初期化している)
        self.in_params = vars(self.args)
        ## @var out_params
        #  出力パラメータの辞書
        self.out_params = dict()
        ## @var in_symlinks
        #  シンボリックリンクを張りたい入力ファイル名を記述する辞書
        self.in_symlinks = dict()
        ## @var out_files
        #  出力ファイル名を記述する辞書
        self.out_files = dict()
        ## @var out_symlinks
        #  シンボリックリンクを張りたい出力ファイル名を記述する辞書
        self.out_symlinks = dict()
        pyfile_str = currentframe().f_back.f_code.co_filename
        abspath_without_ext = splitext(pyfile_str)[0]
        module_name = split(abspath_without_ext)[1]
        self.make_logger(module_name, self.args.verbose, self.args.logfile)
        formatter = Formatter(
            "[%(asctime) -15s]\n%(filename)s,"
            "L%(lineno)s:%(levelname)s\t%(message)s"
        )
        self.set_logger_format(formatter)

    ## ロガーを生成するメソッド
    #
    #  指定の名前のロガーを生成するメソッド.@n
    #  ハンドラとして, 標準出力(StreamHandler)とファイル出力(FileHandler)を登録する.@n
    #  ただし, ログファイル名を指定しなかった場合(logfile_name=Noneの場合)には
    #  ファイル出力は行わない.@n
    #  また, ファイルへのログレベルはDEBUGに設定している.@n
    #  @param self オブジェクト自身に対するポインタ
    #  @param name ロガーの名前
    #  @param level 標準出力のハンドラに対するログレベル
    #  @param logfile_name ログをファイル出力する場合のファイル名
    def make_logger(self, name, level, logfile_name=None):
        ## @var logger
        #  メソッドexcute()内で利用するロガーオブジェクト
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG)
        sh = StreamHandler()
        sh.setLevel(level)
        self.logger.addHandler(sh)
        if logfile_name is not None:
            fh = FileHandler(logfile_name, 'w')
            fh.setLevel(DEBUG)
            self.logger.addHandler(fh)
            self.out_files['log'] = logfile_name
        self.logger.propagate = False

    ## ロガーに対してフォーマッタを設定するメソッド
    #  @param self オブジェクト自身に対するポインタ
    #  @param formatter メンバ変数loggerに設定したいフォーマッタオブジェクト
    def set_logger_format(self, formatter):
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)

    ## メンバ変数in_params, out_params, in_symlinks, out_symlinks, out_filesの
    #  内容に基づいて, jsonファイルを生成するメソッド
    #  @param self オブジェクト自身に対するポインタ
    #  @return io_params_json 入出力パラメータに関するjsonオブジェクト
    #  @return io_files_path_json 出力ファイルおよびシンボリックリンクに関するjsonオブジェクト
    def make_output_json(self):
        def json_callback_deco(func):
            import functools

            @functools.wraps(func)
            def wrapper(o):
                if isinstance(o, file):
                    return o.name
                return func(o)
            return wrapper

        @json_callback_deco
        def skipvalues(o):
            return 'unserializable object'

        @json_callback_deco
        def unskipvalues(o):
            raise TypeError(repr(o) + ' is not JSON serializable')

        if self.args.unskipvalues:
            json_dump_callback = unskipvalues
        else:
            json_dump_callback = skipvalues

        io_params_dict = {
            'input_params': self.in_params,
            'output_params': self.out_params
        }
        io_params_json = json.dumps(
            io_params_dict, indent=4,
            default=json_dump_callback
        )

        io_files_path_dict = {
            'input_symlinks': self.in_symlinks,
            'output_files': self.out_files,
            'output_symlinks': self.out_symlinks,
        }
        io_files_path_json = json.dumps(
            io_files_path_dict, indent=4,
            default=json_dump_callback
        )

        return io_params_json, io_files_path_json

    ## メインの処理を行うメソッド
    #
    #  利用時には継承先のクラスで本メソッドをオーバーライドして利用する.
    #  @param self オブジェクト自身に対するポインタ
    def execute(self):
        """
        計算を行って，self.out_paramsに出力パラメータの値を，
        self.in_filesやself.out_filesには入出力のファイルパスを保存する
        """
        pass

    def make_aggregated_parser(self, parents):
        main_parser = parents[-1]
        prog = main_parser.prog
        description = main_parser.description
        epilog = main_parser.epilog
        version = main_parser.version

        def remove_options(parser, options):
            for option in options:
                for action in parser._actions:
                    action_dict = vars(action)
                    if 'option_strings' in action_dict:
                        opt_strs = action_dict['option_strings']
                        if option in opt_strs:
                            parser._handle_conflict_resolve(
                                None, [(option, action)]
                            )
                            break

        for parser in parents:
            if parser.add_help:
                remove_options(parser, ['--help', '-h'])
                parser.add_help = False

        aggregated_parser = argparse.ArgumentParser(
            prog=prog,
            description=description,
            epilog=epilog,
            version=version,
            parents=parents,
            add_help=True
        )
        aggregated_parser.formatter_class = \
            argparse.ArgumentDefaultsHelpFormatter
        return aggregated_parser

    ## コマンドライン引数のパーサを生成するメソッド
    #
    #  excute()と同様に, 継承先のクラスで本メソッドをオーバーライドして利用する.@n
    #  本メソッドでは, ログに関するコマンドラインオプションのみを定義している.
    #  @param self オブジェクト自身に対するポインタ
    #  @return parser パーサオブジェクト
    def make_parser(self):
        # parserの設定
        parser_decsription = """
        template
        """
        parser = argparse.ArgumentParser(
            description=parser_decsription,
            add_help=False
        )
        g = parser.add_argument_group('program settings')
        verbose_help = 'logging level'
        g.add_argument(
            '-v', '--verbose',
            type=int,
            default=INFO,
            help=verbose_help
        )
        logfile_help = 'log file name'
        g.add_argument(
            '-l', '--logfile',
            type=str,
            default=None,
            help=logfile_help
        )
        unskip_help = \
            'If unskipvalues is set, '\
            'dict values which is not JSON serializable will be skipped '\
            'instead of raise TypeError'
        g.add_argument(
            '--unskipvalues',
            action='store_true',
            help=unskip_help
        )

        return parser

    def parse_args(self, argv, parser_dict):
        parser = self.make_parser()
        parser_dict['main'] = parser
        parents = parser_dict.values()
        aggregated_parser = self.make_aggregated_parser(parents)
        aggregated_parser.parse_args(argv)
        remain_args = argv
        self.args, remain_args = \
            parser_dict['main'].parse_known_args(remain_args)
        for name, parser in parser_dict.items():
            if name != 'main':
                args, remain_args = parser.parse_known_args(remain_args)
                setattr(self.args, name, args)


## main関数
#
#  この関数にtemplate.Mainを継承したオブジェクトを引数として渡し,
#  excute()メソッドを実行する. @n
#  excute()内で例外が発生した場合にはロガーにtracebackの内容を出力する.@n
#  @param obj template.Mainを継承したオブジェクト
#  @return パラメータおよびファイルに関するjsonファイルオブジェクトおよびerrorに関する文字列
def main(obj):
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
    except KeyboardInterrupt:
        error = 'KeyboardInterrupted'
    return obj.make_output_json(), error
