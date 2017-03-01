import argparse
import configparser
import os
import subprocess


DEFAULT_CONF_FILE = os.path.join(os.getenv("HOME"), ".config", "filesync", "filesync.conf")


def check_file(path, host=None):
    if not os.path.isfile(path):
        # specified file is not a file
        return False
    # potential bug:
    # (b'', b'sha256sum: /home/mint/games/snes_msu1/chrono_msu1.sfc: Is a directory\n')
    if host:
        cmd = "ssh {0} sha256sum {1}".format(host, path)
    else:
        cmd = "sha256sum {}".format(path)
    p = subprocess.Popen(cmd.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    c = p.communicate()[0].decode().split()[0]
    return c


def compare_files(file1, file2):
    return file1 == file2


def read_config_file(f):
    c = configparser.ConfigParser()
    c.read(f)

    for s in c.sections():
        if s == "global":
            # Do stuff
            pass
        elif s != "local":
            for o in c.options(s):
                samefile = compare_files(check_file(c["local"][o]), check_file(c[s][o]))
                # print(samefile)
                # print("{0}: {1}: {2}".format(s, o, c[s][o]))
                if samefile:
                    print("{} FILE IS THE SAME".format(o))


def parse_args(args):
    pass


def main():
    # print("Are files the same???!?!")
    # print(compare_files(check_file("/home/larry/games/snes_msu1/chrono_msu1.sfc/save.ram", host="alucard"), check_file("/home/mint/games/snes_msu1/chrono_msu1.sfc/save.ram")))
    read_config_file(DEFAULT_CONF_FILE)


if __name__ == "__main__":
    main()
