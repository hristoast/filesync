import argparse
import configparser
import logging
import os
import shlex
import subprocess
import sys
import textwrap

from datetime import datetime
from typing import Union as T


DEFAULT_CONF_FILE = os.path.join(os.getenv("HOME"), ".config", "filesync", "filesync.conf")
DESCRIPTION = "Sync files between two machines.  Works in either `push` or `pull` modes."
LICENSE = 'GPLv3'
LOGFMT = '==> %(message)s'
PROGNAME = "filesync"
VERSION = "0.6"


class CheckFileAgeException(Exception):
    "Raised when checking a file's age fails."
    pass


class CheckFileShaException(Exception):
    "Raised when checking a file's sha256sum fails."
    pass


class MissingRequiredOptionException(Exception):
    "Raised when a required config option is missing."
    pass


class MissingRequiredSectionException(Exception):
    "Raised when a required config option is missing."
    pass


# def _can_do_colors():
#     return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def check_file_age(path: str, host=None) -> T[str, int]:
    """"""
    if host:
        cli = ['python', '-c',
               'import os; s=os.stat("{}");t=s.st_mtime;print(t)'.format(path)]
        p = subprocess.Popen(cli, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        c = p.communicate()
        if p.returncode != 0:
            print(c[1].decode())
            raise CheckFileAgeException
        return c.decode()[0]
    else:
        stat = os.stat(path)
        return stat.st_mtime


def check_file_sha(path: str, host=None) -> T[bool, str]:
    """"""
    if not host and not os.path.isfile(path):
        # specified file is not a file
        return False
    if host:
        cmd = "ssh {0} sha256sum {1}".format(host, path)
    else:
        cmd = "sha256sum {}".format(path)
    p = subprocess.Popen(cmd.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, error = p.communicate()
    if out:
        return out
    if error:
        raise CheckFileShaException


def compare_files(file1: str, file2: str) -> bool:
    """
    Return True if 'file1' is the same
    as 'file2' or False if not (content-wise).
    """
    return file1 == file2


def emit_log(msg: str, level=logging.INFO, quiet=False, *args, **kwargs):
    if not quiet:
        global VERBOSE
        if not VERBOSE:
            msg = textwrap.shorten(msg, width=int(get_terminal_dims()[0]) - 5,
                                   placeholder="...")
        if level == logging.DEBUG:
            logging.debug(msg, *args, **kwargs)
        elif level == logging.INFO:
            logging.info(msg, *args, **kwargs)
        elif level == logging.WARN:
            logging.warn(msg, *args, **kwargs)
        elif level == logging.ERROR:
            logging.error(msg, *args, **kwargs)


def ensure_required_sections(config: configparser.ConfigParser) -> bool:
    "Return False if all sections are not present in 'config'."
    if 'global' in config.sections() \
       and 'local' in config.sections() \
       and 'remote' in config.sections():
        return True
    else:
        return False


def error_and_die(msg: str) -> SystemExit:
    sys.stderr.write("ERROR: " + msg + " Exiting ..." + "\n")
    sys.exit(1)


def file_sync(direction: str, local_path: str, remote_path: str, host: str) -> T[bool, str]:
    """
    Sync local and remote files given a 'direction'.  If 'pull', a file is
    synced from 'host':'remote_path' to 'local_path'.  If 'push', a file is
    syned from 'local_path' to 'host':'remote_path'.  If the operation is a
    success, 'True' is returned, if not then 'False' is returned.

    Before doing all that, try to locate a local ssh config file, in case there
    are any local configs we should consider in our connection attempts.
    """
    # local_age = check_file_age(local_path)
    # remote_age = check_file_age(remote_path, host=host)

    # emit_log(local_age)
    # emit_log(remote_age)

    rsync = ["rsync", ]
    rsync.append("-aPv")

    # Build the rsync command list as needed for pulling from a remote host
    if direction == "pull":
        rsync.append('{0}:{1}'.format(host, remote_path
                                      .replace(' ', '\\ ')
                                      .replace('(', '\\(')
                                      .replace(')', '\\)')))
        rsync.append('{}'.format(os.path.dirname(local_path)))

    # Or pushing to a remote host.
    elif direction == "push":
        rsync.append('{}'.format(local_path))
        rsync.append('{0}:{1}'.format(
            host, os.path.dirname(remote_path)))

    # Run the rsync
    p = subprocess.Popen(rsync, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    c = p.communicate()
    if p.returncode != 0:
        # The rsync did not succeed for some reason..
        return c[1].decode().rstrip().replace("\n", " ")
    # Everything should have worked.
    # TODO: if verbose return stdout
    return True


def get_terminal_dims() -> tuple:
    tty = os.popen('stty size', 'r')
    y, x = tty.read().split()
    tty.close()
    return x, y


def _is_forced(config: configparser.ConfigParser) -> bool:
    if "force" in config["global"].keys():
        return config["global"]["force"]
    return False


def _is_verbose(config: configparser.ConfigParser) -> bool:
    if "verbose" in config["global"].keys():
        return config["global"]["verbose"]
    return False


def make_backup_file(path: str, host=None) -> T[bool, str]:
    backup = path + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if host:
        cmd = ["ssh", "{}".format(host), "/bin/cp", "-afr",
               "{}".format(shlex.quote(path)), "{}".format(shlex.quote(backup))]
    else:
        cmd = ["/bin/cp", "-afr", "{}".format(path), "{}".format(backup)]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    c = p.communicate()
    if p.returncode != 0:
        return False, c[1].decode()
    return backup


def read_config_file(f: str) -> T[configparser.ConfigParser, int]:
    c = configparser.ConfigParser()
    if c.read(f):
        # Return the loaded config file object
        return c
    else:
        # Couldn't find a file; bail out
        error_and_die("Provide a config file with '-c' or place one at \
'{}'.".format(DEFAULT_CONF_FILE))


def _check_file(d: dict, k: str, padding: int, local: bool, remote: bool) -> bool:
    if local:
        src = "local"
        dest = "remote"
    elif remote:
        dest = "local"
        src = "remote"
    emit_log("{0: <{n}}Checking {1} file...".format(
        k + ':', src, n=padding), level=logging.DEBUG)
    try:
        f = d[k][src]
        emit_log("{0: <{n}}{1} file found: {2}".format(
            k + ':', src.capitalize(), f, n=padding), level=logging.DEBUG)
        return f
    except KeyError:
        f = None
        emit_log(
            "{0: <{n}}No {1} file configured, attempting to mimic {2} path..."
            .format(k + ':', src, dest, n=padding), level=logging.DEBUG)
        return f


def sync_files(config: configparser.ConfigParser, direction: str):
    """
    Sync 'src' to 'dest', or 'dest' to 'src' (depending on the 'direction',)
    but check the sha256sum of each file first to ensure that a sync
    needs to happen to begin with.

    Build up a dict, 'sync_dict' that would look something like this:

    {'wwf no mercy':
        {'remote': '/home/larry/WWF No Mercy (U) (V1.0) [!].fla',
         'local': '/home/larry/fstest/WWF No Mercy (U) (V1.0) [!].fla'},
     'current song':
        {'local': '/home/larry/fstest/current_song2.py'},
     'chrono trigger':
        {'remote': '/home/larry/save.ram',
         'local': '/home/larry/fstest/save.ram'},
     'openmw':
        {'remote': '/home/larry/jaja/openmw'}}

    Then iterate through it and run file_sync() as needed.  If a remote file
    is pulled with no configured local path, or a local file pushed with no
    configured remote path, then an attempt is made to mimic the opposite path
    and do the right thing.
    """
    # Convenience variables
    local = config["local"]
    remote = config["remote"]
    remote_host = config["global"]["remote host"]

    # Build the sync_dict
    sync_dict = {}
    for k, v in local.items():
        sync_dict.update({k: {"local": v}})
    for k, v in remote.items():
        try:
            sync_dict[k]["remote"] = v
        except KeyError:
            # This is a remote file with no configured local file
            sync_dict.update({k: {"remote": v}})

    # Find out our longest config key so terminal output is padded correctly
    l_list = []
    [l_list.append(len(k)) for k in config["local"].keys()]
    l_list.sort()
    l_pad = l_list[-1] + 3  # Pad for a colon and two spaces
    r_list = []
    [r_list.append(len(k)) for k in config["remote"].keys()]
    r_list.sort()
    r_pad = l_list[-1] + 3  # Pad for a colon and two spaces

    # Iterate through the sync_dict, sync as needed
    global VERBOSE
    for key in sync_dict.keys():
        if VERBOSE is True:
            l_pad = len(key) + 3
            r_pad = len(key) + 3

        # Check local file
        local_file = _check_file(sync_dict, key, l_pad, True, False)

        # Check remote file
        remote_file = _check_file(sync_dict, key, r_pad, False, True)

        # No local file, pull command
        if not local_file and direction == "pull":
            synced = file_sync(direction, remote_file,
                               remote_file, host=remote_host)
            if synced is True:
                emit_log("{0: <{n}}\"{1}\" synced from \"{1}\"".format(
                    key + ':', remote_host, remote_file, n=r_pad))
            else:
                emit_log('TODO TODO')#TODO
                # emit_log("{0: <{n}}Unable to sync \"{1}\" from \"{1}\"!".format(
                #     key + ':', remote_host, remote_file, n=r_pad))

        # No remote file, push command
        elif not remote_file and direction == "push":
            synced = file_sync(direction, local_file,
                               local_file, host=remote_host)
            if synced is True:
                emit_log("{0: <{n}}\"{1}\" synced to \"{2}\"".format(
                    key + ':', local_file.split('/')[-1], remote_host, n=l_pad))
            else:
                # TODO: Need to show a meaningful message here...
                emit_log("{0: <{n}}Unable to sync \"{1}\" to \"{1}\"!".format(
                    key + ':', local_file, remote_host, n=l_pad))

        # Both files present
        elif local_file and remote_file:
            synced = file_sync(direction, local_file, remote_file, remote_host)

            # Pull command
            if direction == "pull":
                if synced is True:
                    emit_log("{0: <{n}}\"{1}\" synced from \"{2}\"".format(
                        key + ':', remote_file.split('/')[-1], remote_host, n=r_pad))
                else:
                    emit_log("{0: <{n}}Unable to sync \"{1}\" from \"{2}\"!".format(
                        key + ':', remote_file.split('/')[-1], remote_host, n=r_pad))

            # Push command
            elif direction == "push":
                if synced is True:
                    emit_log("{0: <{n}}\"{1}\" synced to \"{2}\"".format(
                        key + ':', local_file.split('/')[-1], remote_host, n=l_pad))
                else:
                    emit_log("{0: <{n}}ERROR: {1}".format(
                        key + ':', synced, n=l_pad))

        else:  # pull local file with no remote configuration
            if local_file:
                remote_file = local_file
            synced = file_sync(direction, local_file, remote_file, remote_host)
            if direction == "push":
                word = "to"
            elif direction == "pull":
                word = "from"
            if synced is True:
                emit_log("{0: <{n}}\"{1}\" synced {2} \"{3}\"".format(
                    key + ':', remote_file.split('/')[-1], word, remote_host, n=r_pad))
            else:
                emit_log("{0: <{n}}Unable to sync \"{1}\" {2} \"{3}\"!".format(
                    key + ':', remote_file.split('/')[-1], word, remote_host, n=r_pad))


def parse_args(args: list) -> str:
    force = False
    global VERBOSE
    VERBOSE = verbose = False
    parser = argparse.ArgumentParser(description=DESCRIPTION, prog=PROGNAME)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--clean", action="store_true", help="Clean up backup files created during sync")
    # actions.add_argument("-g", "--gen-conf-file", action="store_true",
    #                      help="Print a formatted config file to stdout, formatted from loaded options.")
    actions.add_argument("--pull", action="store_true", help="Sync files from the remote to your local")
    actions.add_argument("--push", action="store_true", help="Sync files from your local to the remote")
    options = parser.add_argument_group("Options")
    options.add_argument("-H", "--host", help="Specify a remote host to sync to", metavar="REMOTE HOST")
    options.add_argument("-L", "--local-file", help="Specify a local file to sync when pushing",
                         metavar="LOCAL FILE")
    options.add_argument("-R", "--remote-file", help="Specify a remote file to sync when pulling",
                         metavar="REMOTE FILE")
    options.add_argument("-c", "--conf", help="Optionally specify a config file.",
                         metavar="CONFIG FILE")
    options.add_argument("--force", action="store_true",
                         help="Force removal of backup files when 'gvfs-trash' is not available")
    # TODO: single file sync option; specify the keyname of the single file
    options.add_argument("-v", "--verbose", action="store_true", help="Show extra logging messages")
    parser.add_argument("--version", action="version", version=VERSION, help=argparse.SUPPRESS)
    parsed_args = parser.parse_args(args)

    # Options
    if parsed_args.conf:
        # Read the passed-in config file
        c = read_config_file(parsed_args.conf)
    elif not parsed_args.conf:
        # Read the default config file
        c = read_config_file(DEFAULT_CONF_FILE)
    if parsed_args.force:
        # Force rm'ing backup files
        force = True
    if parsed_args.host:
        c["global"]["remote host"] = parsed_args.host
    if parsed_args.verbose:
        verbose = True

    # Check for optional global settings
    if not force:
        force = _is_forced(c)
    if not verbose:
        verbose = _is_verbose(c)

    if verbose:
        VERBOSE = True
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(format=LOGFMT, level=log_level, stream=sys.stdout)
    emit_log("BEGIN filesync run at {}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")), level=logging.DEBUG)
    emit_log("Force: {}".format(force), level=logging.DEBUG)
    emit_log("Verbose: {}".format(verbose), level=logging.DEBUG)

    def _unpack_file_args(arg: str) -> T[list, SystemExit]:
        try:
            name, path = arg.split(":")
        except ValueError:
            error_and_die("This needs to be formatted like: \"NAME:/PATH.txt\".")
        return name, path

    if parsed_args.local_file:
        name, path = _unpack_file_args(parsed_args.local_file)
        c['local'].update({name: path})
    if parsed_args.remote_file:
        name, path = _unpack_file_args(parsed_args.remote_file)
        c['remote'].update({name: path})

    # TODO: set up options read from config file here
    # TODO: also ensure we have all required options

    # Actions
    if parsed_args.clean:
        # Clean out backup files
        print("CLEAN!")
    elif parsed_args.pull:
        # Pull files from the remote host
        sync_files(c, "pull")
    elif parsed_args.push:
        # Push files to the remote host
        sync_files(c, "push")
    else:
        parser.print_usage()
    emit_log("END filesync run at {}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")), level=logging.DEBUG)


def main():
    # TODO: catch KeyboardInterrupt
    parse_args(sys.argv[1:])


if __name__ == '__main__':
    main()
