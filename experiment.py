#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import os
import sys
import datetime
from exp_wrapper import gitlog
import json
import shutil
import glob
import re
import logging
import errno


def make_parser():
    # parserの設定
    parser_description = """
    Experiment wrapper script.\n
    This script manage input/output parameters and files.\n
    If the target script is managed by git,
    this script also output the git repository infomation.
    Inorder to distinguish this experiment wrapper script
    option from the target script option,
    the prefix chars of this script option is set to '+'.
    """

    parser = argparse.ArgumentParser(
        description=parser_description,
        prefix_chars='+',
        fromfile_prefix_chars='@',
        prog='experiment_wrapper'
    )

    pyfile_help = """
    target python script to excute
    """
    parser.add_argument(
        '+p', '++pyfile',
        type=str,
        required=True,
        help=pyfile_help
    )

    root_help = """
    root directory of the experiment
    """
    parser.add_argument(
        '+r', '++root',
        type=str,
        default='./output',
        help=root_help
    )

    comment_help = """
    comment statement
    """
    parser.add_argument(
        '+c', '++comment',
        type=str,
        default=None,
        help=comment_help
    )

    verbose_help = 'show logging info'
    parser.add_argument(
        '+v', '++verbose',
        action='store_true',
        default=False,
        help=verbose_help
    )

    return parser


def dynamic_import(pyfile_str):
    abspath = os.path.abspath(pyfile_str)
    abspath_without_ext = os.path.splitext(abspath)[0]
    dir, module_name = os.path.split(abspath_without_ext)
    logging.info('direcotry of target script: %s' % dir)
    logging.info('module name of target script: %s' % module_name)
    sys.path.append(dir)
    try:
        module = __import__(module_name)
        logging.info('target module has been loaded')
    except ImportError:
        logging.error('No module named %s' % module_name)
    return [module_name, module]


def make_outputdir(root_str, module_name, date_str):
    tdatetime = datetime.datetime.now()
    date_str = tdatetime.strftime('%Y%m%d_%H%M_%S')
    output_dir = os.path.join(root_str, module_name, date_str)
    try:
        os.makedirs(output_dir)
        logging.info('%s has been created' % output_dir)
    except OSError as e:
        logging.exception(e)
        if e.errno != errno.EEXIST:
            raise
        pass
    return output_dir


def save_args(allargs_, output_dir):
    allargs = []
    for arg in allargs_:
        pattern = r"^\@"
        if re.match(pattern, arg):
            with open(arg[1:], 'r') as f:
                lines = f.read().split('n')
                for line in lines:
                    allargs.append(line)
        else:
            allargs.append(arg)
    logging.info('\ncommand line options: %s' % allargs)
    argfile_path = os.path.join(output_dir, 'args.txt')
    with open(argfile_path, 'w') as f:
        for arg in allargs:
            f.write(arg)
            f.write('\n')
    logging.info('%s has been created' % argfile_path)


def save_comment(comment, output_dir, date_str):
    if comment is not None:
        comment_file_path = os.path.join(
            output_dir, 'comment_%s.txt' % date_str
        )
        with open(comment_file_path, 'w') as f:
            f.write(comment)
        logging.info('%s has been created' % comment_file_path)


def save_io_to_json(io_params, io_files, output_dir, date_str):
    io_params_json_path = os.path.join(
        output_dir, 'io_params_%s.json' % date_str
    )
    with open(io_params_json_path, 'w') as f:
        f.write(io_params)
    logging.info('%s has been created' % io_params_json_path)
    io_files_json_path = os.path.join(
        output_dir, 'io_files_%s.json' % date_str
    )
    with open(io_files_json_path, 'w') as f:
        f.write(io_files)
    logging.info('%s has been created' % io_files_json_path)
    io_files_dict = json.loads(io_files)
    return io_files_dict


def make_symboliclink(symlink_list, output_dir, dir_name):
    input_files_link_dir = os.path.join(output_dir, dir_name)
    try:
        os.makedirs(input_files_link_dir)
        logging.info('%s has been created' % input_files_link_dir)
    except OSError as e:
        logging.exception(e)
        if e.errno != errno.EEXIST:
            raise
        pass
    for target, source in symlink_list.items():
        if os.path.exists(source):
            target_path = os.path.join(input_files_link_dir, target)
            os.symlink(source, target_path)
            logging.info(
                'symbolic link %s has been created' % target_path
            )


def move_output(output_files, output_dir):
    output_files_dir = os.path.join(output_dir, 'output_files')
    try:
        os.makedirs(output_files_dir)
        logging.info('%s has been created' % output_files_dir)
    except OSError as e:
        logging.exception(e)
        if e.errno != errno.EEXIST:
            raise
        pass
    for output_file in output_files.values():
        if os.path.exists(output_file):
            ofiles = glob.glob('%s*' % output_file)
            for ofile in ofiles:
                shutil.move(ofile, output_files_dir)
                logging.info('%s has been moved' % ofile)


def main():
    # パーサーの生成
    parser = make_parser()

    # コマンドラインオプションをパース
    args, undefined_argv = parser.parse_known_args()

    # ログの出力レベルの設定
    if args.verbose:
        format = "[%(asctime) -15s]\n%(filename)s,"\
            "L%(lineno)s:%(levelname)s\t%(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=format
        )

    # 実行するpythonファイルの動的import
    module_name, module = dynamic_import(args.pyfile)

    # スクリプト実行日時の文字列を取得
    tdatetime = datetime.datetime.now()
    date_str = tdatetime.strftime('%Y%m%d_%H%M_%S')

    # 実験ファイルの出力ディレクトリを作成
    output_dir = make_outputdir(args.root, module_name, date_str)

    # コマンドラインオプションのパース情報をファイルに保存
    save_args(sys.argv[1:], output_dir)

    # コメントファイルの作成
    save_comment(args.comment, output_dir, date_str)

    # 実行するpythonファイルのコミット情報を出力
    gitlog.write_commitlog(os.path.abspath(args.pyfile), output_dir)

    # pythonファイルを実行
    (io_params, io_files), error_str = module.main(undefined_argv)

    if error_str:
        new_output_dir = output_dir + '_' + error_str
        shutil.move(output_dir, new_output_dir)
        output_dir = new_output_dir
        if error_str is not 'KeyboardInterrupted':
            logging.error('unexpected error at %s' % module_name)
        else:
            logging.error('KeyboardInterrupt')

    # 入出力を表示(jsonを想定)
    logging.info('\n' + io_params.__str__())
    logging.info('\n' + io_files.__str__())

    # 入出力をjsonファイルに保存
    io_files_dict = save_io_to_json(io_params, io_files, output_dir, date_str)

    # 入力ファイルのシンボリックリンクを作成
    make_symboliclink(
        io_files_dict['input_symlinks'], output_dir, 'input_symlinks'
    )

    # 出力ファイルの移動
    move_output(io_files_dict['output_files'], output_dir)

    # 出力ファイルのシンボリックリンクを作成
    make_symboliclink(
        io_files_dict['output_symlinks'], output_dir, 'output_symlinks'
    )


if __name__ == '__main__':
    main()
