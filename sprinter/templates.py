"""
A storage area for templates as strings
"""

# utils.sh is the same for every namespace, only sourced once
shell_utils_template = """
# don't add paths repeatedly to env vars
# __sprinter_prepend_path "/foo"         => "/foo:$PATH"
# __sprinter_prepend_path "/foo" MANPATH => "/foo:$MANPATH"
__sprinter_prepend_path() {
    local sp_dir="$1"
    local sp_var="${2:-PATH}"
    local sp_list=$(eval echo '$'$sp_var)
    if [ -d "$sp_dir" ]; then
        # strip sp_dir from sp_list
        sp_list=`echo -n $sp_list | awk -v RS=: -v ORS=: '$0 != "'$sp_dir'"' | sed 's/:$//'`
        # :+ syntax avoids dangling ":" in exported var
        export $sp_var="${sp_dir}${sp_list:+":$sp_list"}"
    fi
}

# remove a path from env var (default PATH)
__sprinter_remove_path() {
    local sp_dir="$1"
    local sp_var="${2:-PATH}"
    local sp_list=$(eval echo '$'$sp_var)
    # strip sp_dir from sp_list
    export $sp_var=$(echo -n $sp_list | awk -v RS=: -v ORS=: '$0 != "'$sp_dir'"' | sed -E 's/^:|:$//g')
}
"""

source_template = """[ -r "%s" ] && . %s\n"""

warning_template = """
__          __     _____  _   _ _____ _   _  _____
\ \        / /\   |  __ \| \ | |_   _| \ | |/ ____|
 \ \  /\  / /  \  | |__) |  \| | | | |  \| | |  __
  \ \/  \/ / /\ \ |  _  /| . ` | | | | . ` | | |_ |
   \  /\  / ____ \| | \ \| |\  |_| |_| |\  | |__| |
    \/  \/_/    \_\_|  \_\_| \_|_____|_| \_|\_____|
"""
