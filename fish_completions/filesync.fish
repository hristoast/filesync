# completion for filesync

set c filesync

complete -c $c -l clean -d "Clean up backup files created during sync"
complete -c $c -l conf -s c -d "Optionally specify a config file."
complete -c $c -l force -d "Force removal of backup files when 'gvfs-trash' is not available"
complete -c $c -l help -s h -d "Show the help and exit"
complete -c $c -l host -s H -d "Specify a remote host to sync to"
complete -c $c -l local-file -s L -d "Specify a local file to sync when pushing"
complete -c $c -l remote-file -s R -d "Specify a remote file to sync when pulling"
complete -c $c -l pull -d "Sync files from the remote to your local"
complete -c $c -l push -d "Sync files from your local to the remote"
complete -c $c -l verbose -s v -d "Show extra logging messages"
complete -c $c -l version -d "Show the version number and exit"
