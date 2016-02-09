# -*- coding:utf-8 -*-
import json
import argparse
from logging import getLogger
from logging import StreamHandler, FileHandler
from logging import INFO, DEBUG
from logging import Formatter
from inspect import currentframe
from os.path import splitext, split


class Main(object):
    def __init__(self, argv):
        parser = self.make_parser()
        self.args = parser.parse_args(argv)
        self.in_params = vars(self.args)
        self.out_params = dict()
        self.in_symlinks = dict()
        self.out_files = dict()
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

    def make_logger(self, name, level, logfile_name=None):
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

    def set_logger_format(self, formatter):
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)

    def make_output_json(self):
        io_params_dict = {
            'input_params': self.in_params,
            'output_params': self.out_params
        }
        io_params_json = json.dumps(io_params_dict, indent=4)

        io_files_path_dict = {
            'input_symlinks': self.in_symlinks,
            'output_files': self.out_files,
            'output_symlinks': self.out_symlinks,
        }
        io_files_path_json = json.dumps(io_files_path_dict, indent=4)

        return io_params_json, io_files_path_json

    def execute(self):
        """
        計算を行って，self.out_paramsに出力パラメータの値を，
        self.in_filesやself.out_filesには入出力のファイルパスを保存する
        """
        pass

    def make_parser(self):
        # parserの設定
        parser_decsription = """
        template
        """
        parser = argparse.ArgumentParser(
            description=parser_decsription
        )
        verbose_help = 'logging level'
        parser.add_argument(
            '-v', '--verbose',
            type=int,
            default=INFO,
            help=verbose_help
        )
        logfile_help = 'log file name'
        parser.add_argument(
            '-l', '--logfile',
            type=str,
            default=None,
            help=logfile_help
        )

        return parser


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