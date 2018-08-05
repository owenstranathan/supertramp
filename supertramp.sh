#!/bin/bash

readonly PROGNAME="$(basename "$0")"

[[ $TRACE ]] && set -x

function errcho() {
    echo "$@" >&2
}

function usage() {
    errcho -e "$PROGNAME [bduclm] <source>

<source>
    either a url to a remote git repo or a path to a local git repo

Clones the <source> git repo temporarily if remote and performs the options on it

Options
    -c
        use caching (clones the repo to a permanent cache directory 
        /tmp/supertramp/cache), use this option to speed up supsequent builds

    -b[<branch>]
        checkout the remote at source at <branch>

    -l[<log-path>]
        store output of make commands to <log-path>

    -m[<command1>,<command2>,...,<commandn>]
        extra make commands to run 

Examples:
    supertramp -m \"build,deploy\" https://owiewestside:$GITHUB_TOKEN@github.com/owenstranathan/supertramp
        clone and run make [build and deploy in that order]
"
}

function parse_args() {
    MAKE_COMMANDS=()
    while getopts ":cb:e:l:m:" option; do
        case $option in 
            b) # Branch
                BRANCH="$OPTARG"
                ;;
            c) # Cache
                CACHE_SOURCE=true
                ;;
            e) # Env file
                ENV_FILE="$OPTARG"
                ;;
            l) # Log
                LOG_PATH="$OPTARG"
                ;;
            m) # make command
                SAVE_IFS=$IFS
                IFS=','
                for command in $OPTARG; do
                MAKE_COMMANDS+=("$command")
                done
                IFS=$SAVE_IFS
                ;;
            *)
                usage
                ;;
        esac
    done
    shift $((OPTIND-1))
    if [[ ! "$1" ]]; then
        errcho -e "$usage"
        exit 1
    fi
    SOURCE="$1"
}

function main() {
    SOURCE_NAME="$(basename "$SOURCE")"

    if [[ "$SOURCE" =~ (git@|http:\/\/|https:\/\/)(github.com)(:|\/)(.*)(\/)(.*).?($|git$)? ]]; then
        REMOTE=true
        if [[ ! $CACHE_SOURCE ]]; then
            DIR="$(mktemp -d)"
            trap "rm -rf $DIR" INT TERM EXIT
        else
            DIR="/tmp/supertramp/$SOURCE_NAME"
            mkdir -p "$DIR"
        fi
    elif [ -d "$SOURCE" ]; then
        REMOTE=false
    else
        errcho "Invalid source!"
        exit 1
    fi

    if [[ "$REMOTE" == true ]]; then
        if [[ ! "$CACHE_SOURCE" ]]; then
            if [[ "$BRANCH" ]]; then
                git clone -b "$BRANCH" "$SOURCE" "$DIR"
            else
                git clone "$SOURCE" "$DIR"
            fi
        else
            if [[ -d "$DIR" ]]; then
                git reset --hard HEAD --work-tree="$DIR"
                if git pull --work-tree="$DIR" --rebase; then
                    if [[ "$BRANCH" ]]; then
                        git clone -b "$BRANCH" "$SOURCE" "$DIR"
                    else
                        git clone "$SOURCE" "$DIR"
                    fi
                else
                    errcho "Failed to pull from upstream"
                fi
            fi
            # TODO check if cached directory exists and try to pull
        fi
    else
        if [[ "$BRANCH" ]]; then
            git --work-tree="$DIR" checkout "$BRANCH"
        fi
    fi

    if [ -f "$DIR/.env" ]; then
        echo "Detected .env environment variables"
        echo "Loading .env environment variables"
        export "$(grep -v '^#' "$dir/.env" | xargs)"
    elif [[ -f $ENV_FILE ]]; then
        echo "Loading $ENV_FILE environment variables"
        export "$(grep -v '^#' "$ENV_FILE" | xargs)"
    fi

    for COMMAND in "${MAKE_COMMANDS[@]}"; do
        make "$COMMAND" -C "$DIR"
    done

}

parse_args "$@"    
if [[ "$LOG_PATH" ]]; then
    main 2>&1 | tee "$LOG_PATH"
else
    main
fi