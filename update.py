#!/usr/bin/env python3
# coding: utf8

# Author: Lenz Furrer, 2018


'''
Add a new set of results to the tracker.
'''


import re
import os
import sys
import time
import argparse
import subprocess as sp


HERE = os.path.dirname(__file__)

BRANCH = 'master'
REMOTE = 'origin'
REMOTE_URL = 'https://github.com/en-dash/disease-normalization'


def main():
    '''
    Run as script: read results from STDIN.
    '''
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        '-p', '--pull', action='store_true',
        help='pull from the remote tracker repo before updating')
    ap.add_argument(
        '-u', '--push', action='store_true',
        help='push to the remote tracker repo after updating')
    ap.add_argument(
        '-m', '--message',
        help='use this instead of the commit message')
    args = ap.parse_args()
    run(sys.stdin.read(), **vars(args))


def run(summary, pull=False, push=False, message=None):
    '''
    Process the result summary and update the repo.
    '''
    if pull or push:
        _git('pull', REMOTE, BRANCH)
    hash_, msg, results, conf = _parse(summary)
    if message is None:
        message = msg.split('\n')[0]
    score = _main_score(results)
    _add_data(message, ['results', 'config'], [results, conf])
    _update_table('README.md', hash_, message, score)
    if push:
        _git('push', REMOTE, BRANCH)


def _parse(summary):
    m = re.match(r'''
        \#\ Commit\ hash: (.+?)
        \#\ Commit\ message: (.+?)
        \#\ Results: (.+?)
        \#\ Configuration: (.+)
        ''', summary, re.DOTALL | re.VERBOSE)
    return [hunk.strip() for hunk in m.groups()]


def _main_score(results):
    acc = float(results.split()[1])
    return '{:.4}'.format(acc)


def _add_data(msg, filenames, contents):
    for fn, content in zip(filenames, contents):
        with open(os.path.join(HERE, fn), 'w', encoding='utf8') as f:
            f.write(content)
            f.write('\n')
    _git('add', *filenames)
    _git('commit', '-m', '{} (data)'.format(msg), '--allow-empty')


def _update_table(filename, hash_, msg, score):
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    local_link = '[diff](../../commit/{})'.format(_get_hash())
    remote_link = '[original]({}/commit/{})'.format(REMOTE_URL, hash_)
    row = ' | '.join([date, msg, score, local_link, remote_link]) + '\n'
    with open(filename, 'a', encoding='utf8') as f:
        f.write(row)
    _git('add', filename)
    _git('commit', '-m', '{} (table)'.format(msg))


def _git(*args):
    print('git', *args)
    sp.run(['git', *args], check=True, cwd=HERE)


def _get_hash():
    args = ['git', 'log', '-1', '--pretty=%H']
    compl = sp.run(args, stdout=sp.PIPE, check=True, cwd=HERE)
    return compl.stdout.decode('utf8').strip()


if __name__ == '__main__':
    main()
