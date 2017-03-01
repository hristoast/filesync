# filesync

Sync files between two machines.  Works in either `push` or `pull` modes, configure via command line arguments or a config file:

    [global]
    remote host: some-host.tld

    [local]
    File One: /path/to/a/file.txt
    File Two: /path/to/a/game.save

    [remote]
    File One: /path/to/a/file.txt
    File Two: /path/to/a/game.save

To sync to a remote host:

    filesync --push

To sync to your local host:

    filesync --pull

The above two commands assume you've got a valid config file (as seen above, but with real paths to real files) at `$HOME/.config/filesync/filesync.conf`.  If you don't, you can specify one with `-c`.  See [below](#usage) or use `--help` for more information.

## Requirements

`filesync` assumes you can connect to your `remote host` via ssh and makes no attempt to ensure this outside of reading a local ssh config file, if it exists.  Special ports, hostnames, users, or any other requirement you have for connecting should be set there.

The only other requirements are a modern Python 3, and that `rsync` is installed somewhere in `$PATH`.

## Installation

### pip

To install with `pip`, run `make` from the root of this repository.

### binary

To produce a binary executable (as well as a sha256sum), run `make exe`.

## Usage

Command line options override config file options, so a configured `remote host` would be overriden with `--host domain.tld`.

Sync a file from a remote host using no config file:

    filesync --host someplace.host.tld --local-file "my file:~/file.txt" --remote-file "my file":/mnt/file.txt --pull

Sync a file to a remote host using a complete config file:

    filesync --conf ~/my.conf --push

Sync a file to a remote host using a partial config file:

    filesync --conf ~/host1.conf --local-file "source file:~/git/stuff/src.tar.gz" --remote-file "source file:/opt/stuff.tar.gz" --push

You could make a host-specific alias like this for `bash`:

    function host1-sync() {
        filesync --conf ${HOME}/.config/filesync/host1.conf "${@}"
    }
    
Or this for `fish`:

    function host1-sync
        filesync --conf $HOME/.config/filesync/host1.conf $argv
    end

## Why?

Once upon a time, I used to use stuff like ownCloud to achieve a sort of self-hosted game save cloud.  It worked well enough and I of course used it for non-game files as well.  All that comes with the setup and continued maintenance cost of that system, which ultimately I gave up on.

`filesync` began as a small shell script with some hard-coded paths which synced my Chrono Trigger saves between a desktop machine and a laptop.
