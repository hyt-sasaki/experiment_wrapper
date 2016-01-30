# -*- coding:utf-8 -*-
import datetime
import codecs
import os
import git


class gitlog(object):
    def __init__(self, repo, branch=None):
        self.repo = repo
        self.file = file
        if branch is None:
            branch = self.repo.active_branch.name
        try:
            self.latest_commit =\
                repo.iter_commits(branch, max_count=100).next()
        except Exception as e:
            print e.message
            self.latest_commit = None
            raise e

    def write_commit(self, f, verbose=False):
        if self.latest_commit is None:
            if verbose:
                print '最新のコミットが存在しません'
            return
        hash_line = u'ハッシュID: %s \n' % (self.latest_commit.hexsha)
        message_line = u'メッセージ: %s' % (self.latest_commit.message)
        committed_date = self.latest_commit.committed_date
        committed_date = datetime.datetime.fromtimestamp(committed_date)
        committed_date_line = u'コミット日時: %s \n' % (committed_date)
        stats_line = u'Diff: 実行時のソースコードと上記コミットとの差分\n%s' % \
            (self.repo.git.diff(self.latest_commit.tree))

        f.write(hash_line)
        f.write(message_line)
        f.write(committed_date_line)
        f.write('----------------\n')
        f.write(stats_line)
        if verbose:
            print u'%s の書き込みに成功しました' % f.name
            print '============'
            print hash_line
            print message_line
            print committed_date_line
            print stats_line
            print '============'


def make_repo(script_path, depth=5):
    dir = os.path.dirname(script_path)
    path = os.path.abspath(dir)
    repo_exist = False
    for i in range(depth):
        try:
            repo = git.Repo(path)
            repo_exist = True
            break
        except git.exc.InvalidGitRepositoryError:
            path = os.path.split(path)[0]

    if not repo_exist:
        return None

    tracked_files = [
        os.path.join(repo.working_dir, fn[0])
        for fn in repo.index.entries.keys()
    ]

    script_abspath = os.path.abspath(script_path)

    right_repo = False
    for tracked_file in tracked_files:
        if os.path.samefile(tracked_file, script_abspath):
            right_repo = True
            break

    if not right_repo:
        return None

    return repo


def write_commitlog(
    script_path, filepath=None, branch=None, verbose=False
):
    # リポジトリの取得
    repo = make_repo(script_path)
    # リポジトリが存在しない場合は終了
    if repo is None:
        if verbose:
            print 'リポジトリが存在しません'
        return
    # ブランチの設定
    if branch is None:
        branch = repo.active_branch.name

    # filepathがNoneもしくはディレクトリの場合には，自動的にファイル名を作成
    if filepath is None:
        filepath = './'
    if os.path.isdir(filepath):
        import datetime
        tdatetime = datetime.datetime.now()
        date_str = tdatetime.strftime('%Y%m%d_%H%M')
        fpath = 'commitlog_%s.txt' % date_str
        if filepath is not None:
            dir = filepath
        fpath = os.path.join(dir, fpath)
    else:
        fpath = filepath

    try:
        # gitlogインスタンスを生成
        glog = gitlog(repo, branch)
        # 書き込みファイルをutf-8で開く
        f = codecs.open(fpath, 'w', 'utf-8')
        # commitlogの書き込み
        glog.write_commit(f, verbose)
        # ファイルを閉じる
        f.close()
    except Exception as e:
        print e.message
        print 'コミットログファイルの生成に失敗しました'
