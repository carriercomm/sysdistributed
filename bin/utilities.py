
import sys
import os
import re
import subprocess
from subprocess import PIPE

__all__ = ['execute', 'node_usage', 'copy_to_node', 'SYSDISTRIBUTED',
    'decode_node', 'PIPE']

SYSDISTRIBUTED = os.environ.get('SYSDISTRIBUTED')


def node_usage ():
    print('   Nodes: USER@[HOST]:PORT:DIRECTORY', file=sys.stderr)
    print('       Note: The brackets above are literal brackets.',
        file=sys.stderr)



def decode_node (node):
    match = re.match(r'^([^@]*)@\[([^\]]*)\]:(\d+):(.*)$', node)
    if match == None:
        return False
    user, host, port, directory = match.groups()
    return user, host, port, directory



def execute (command, *argv,
    stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    if command in os.listdir(
        os.path.join(SYSDISTRIBUTED, 'bin')):
        command = os.path.join(SYSDISTRIBUTED, 'bin', command)
    proc = subprocess.Popen([command] + list(argv),
        stdin=stdin, stdout=stdout, stderr=stderr)
    return proc


def copy_to_node (node, fname, content):
    if type(content) == str:
        content = bytes(content, 'utf-8')
    remotesum = b''
    localsum = b''
    command = 'cat >"%s"; sha512sum <"%s"' % (fname, fname)
    if hasattr(content, 'fileno'): # Is an open file.
        content.seek(0)
        remotesum, _ = execute('run-node', node, command,
            stdin=content, stdout=PIPE).communicate()
        content.seek(0)
        localsum, _ = execute('sha512sum',
            stdin=content, stdout=PIPE).communicate()
    elif type(content) == bytes:
        remotesum, _ = execute('run-node', node, command,
            stdin=PIPE, stdout=PIPE).communicate(content)
        localsum, _ = execute('sha512sum',
            stdin=PIPE, stdout=PIPE).communicate(content)
    return remotesum == localsum and \
        re.match(b'^[0-9a-fA-F]{128} ', localsum) != None

