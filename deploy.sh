#!/bin/bash

PROJECT_NAME="lexin"
CURRENT_PATH="$(pwd)"
USER=$(whoami)
GROUP=$(id -g -n $USER)
PROJECT_REPOS="https://github.com/pzyyll/lexi-navigator-server-api.git"

color_echo() {
    # 定义颜色
    local style=0
    case $3 in
    "bold") style="1" ;;      # 粗体或高亮
    "lighten") style="2" ;;   # 次亮
    "italic") style="3" ;;    # 斜体，并非所有的终端都支持
    "underline") style="4" ;; # 下划线
    "blink") style="5" ;;     # 闪烁
    "reverse") style="7" ;;   # 反显
    "conceal") style="8" ;;   # 隐匿
    "strike") style="9" ;;    # 删除线, 并非所有的终端都支持
    *) style="0" ;;
    esac

    local COLOR_PREFIX="\033[${style};"
    local RESET='\033[0m'

    case "$2" in
    "red") echo -e "${COLOR_PREFIX}31m$1${RESET}" ;;
    "green") echo -e "${COLOR_PREFIX}32m$1${RESET}" ;;
    "yellow") echo -e "${COLOR_PREFIX}33m$1${RESET}" ;;
    "blue") echo -e "${COLOR_PREFIX}34m$1${RESET}" ;;
    "purple") echo -e "${COLOR_PREFIX}35m$1${RESET}" ;;
    "cyan") echo -e "${COLOR_PREFIX}36m$1${RESET}" ;;
    "white") echo -e "${COLOR_PREFIX}37m$1${RESET}" ;;
    *) echo -e "$1" ;;
    esac
}

check_python_version() {
    export PYTHON="$1"
    local check_version="$2"

    if [ -z "$PYTHON" ]; then
        if command -v python3 &>/dev/null; then
            PYTHON=python3
        elif command -v python &>/dev/null; then
            PYTHON=python
        else
            echo "Python is not installed. Please install Python 3."
            return 1
        fi
    elif [ ! -x "$PYTHON" ]; then
        echo "The provided Python path '$PYTHON' is not an executable."
        return 1
    fi

    # 检查 Python 可执行文件
    if ! $PYTHON -c '' &>/dev/null; then
        echo "The provided Python path '$PYTHON' is not valid"
        return 1
    fi

    # 检查 Python 版本
    # echo "Checking Python version >= $check_version"
    local pcheck=$(echo $check_version | sed 's/\./,/g')
    # echo "pcheck: $pcheck"
    local is_gt=$($PYTHON -c "import sys; print(sys.version_info >= (${pcheck}))")
    if [ "$is_gt" = "True" ]; then
        echo "$PYTHON"
        return 0
    else
        echo "Found Python, but it is not Python 3. Detected version: Python $($python_cmd --version)"
        return 1
    fi
}

get_python_env() {
    PYTHON=$(check_python_version "${1}" 3.8)
    if [ ! "$?" -eq 0 ]; then
        echo "要求版本 Python >= 3.8。如果你已经安装，可以提供其安装路径给我。"
        while true; do
            read -p "输入：/path/to/your/bin/python3，或者回车退出：" PYTHON
            if [ -z "$PYTHON" ]; then
                color_echo "See you next time! :)" green
                exit_status 1
            fi
            check_python_version "$PYTHON" 3.8
            if [ "$?" -eq 0 ]; then
                break
            else
                echo "提供的 Python 路径未检测到，请重新输入..."
            fi
        done
    fi
    color_echo "Python version is OK: $($PYTHON --version)" yellow
}

check_git() {
    # 检查 Git 是否已安装
    if ! command -v git &>/dev/null; then
        if ! prompt_yes_or_no "Git 未安装。是否尝试安装？"; then
            echo "See you next time! :)"
            exit_status 1
        fi
        echo "正在安装 Git..."
        # 检测操作系统
        OS="$(uname -s)"
        case "${OS}" in
        Linux*) os=Linux ;;
        Darwin*) os=Mac ;;
        # CYGWIN*)    os=Cygwin;;
        # MINGW*)     os=MinGw;;
        *) os="UNKNOWN:${OS}" ;;
        esac

        echo "检测到的操作系统：${os}"

        # 根据操作系统安装 Git
        case "${os}" in
        Linux)
            if [ -f /etc/debian_version ]; then
                # 基于 Debian 的系统
                sudo apt-get update
                sudo apt-get install git -y
            elif [ -f /etc/redhat-release ]; then
                # 基于 RedHat 的系统
                sudo yum update
                sudo yum install git -y
            else
                color_echo "未检测到当前系统可用安装包, 请手动安装 Git: https://git-scm.com/downloads" red

            fi
            ;;
        Mac)
            # 使用 Homebrew 安装 Git
            which -s brew
            if [[ $? != 0 ]]; then
                # 安装 Homebrew
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install git
            ;;
        *)
            color_echo "未检测到当前系统可用安装包, 请手动安装 Git: https://git-scm.com/downloads" red
            ;;
        esac
    else
        color_echo "Git 版本：$(git --version)" yellow
    fi
}

mk_dir() {
    local dir="$1"
    local user=${USER:-$(whoami)}
    local group=$(id -gn $user)

    if [ -d "$dir" ]; then
        echo "Directory $dir already exists."
        return 1
    fi

    local root_dir="$dir"   # return the first directory that does not exist
    local parent_dir=$(dirname "$dir")

    while [ ! -d "$parent_dir" ]; do
        root_dir="$parent_dir"
        parent_dir=$(dirname "$parent_dir")
    done

    if sudo mkdir -p "$dir"; then
        echo "$root_dir"
        sudo chown -R $user:$group "$root_dir"
        return 0
    else
        echo "Failed to create directory $dir."
        return 1
    fi
}

prompt_yes_or_no() {
    while true; do
        read -p "$1 $(color_echo "[yes/no]" yellow italic): " answer
        case $answer in
            [Yy][Ee][Ss])
                return 0
                ;;
            [Nn][Oo])
                return 1
                ;;
            *)
                echo "Invalid input. Enter 'yes' or 'no'."
                ;;
        esac
    done
}

exit_status() {
    local status=$1
    if [ "$status" -eq 0 ]; then
        color_echo "Done!" green
    else
        color_echo "Failed!" red
    fi
    exit $status
}

initialize_variables() {
    # 初始化变量
    if [ -z "$PROJECT_PATH" ]; then
        PROJECT_PATH=$CURRENT_PATH
    fi
    DEPS_REQUIREMENTS_FILE="$PROJECT_PATH/requirements.txt"
}

# Install dependencies
init_pyenv() {
    color_echo "Initializing python running deps..."

    cd $PROJECT_PATH || exit_status 1

    color_echo "Start installing python venv ..."
    # echo "Current python path: $PYTHON"
    init_venv=true
    if [ -d .venv ]; then
        if ! prompt_yes_or_no "The python venv already exists. Remove and re-initialize?"; then
            init_venv=false
        fi
    fi
    if [ "$init_venv" == "true" ]; then
        $PYTHON -m pip install --upgrade pip || exit_status 1
        $PYTHON -m pip install virtualenv --user
        $PYTHON -m venv .venv
    fi

    color_echo "Start installing python deps ..." yellow
    source .venv/bin/activate
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install -r $DEPS_REQUIREMENTS_FILE
}

run() {
    color_echo "Running server..."
    cd $PROJECT_PATH || exit_status 1
    source .venv/bin/activate
    $PYTHON run.py
}

init_submodule() {
    git submodule update --init --recursive || exit_status 1
}

init_conf() {
    cd $PROJECT_PATH || exit_status 1
    source .venv/bin/activate
    python ./tools/deploy.py init-conf
}

init_service() {
    cd $PROJECT_PATH || exit_status 1
    source .venv/bin/activate
    PY=$(which python)
    sudo $PY ./tools/deploy.py init-service
}

run_mongodb() {
    sudo mongod --config /etc/mongod.conf --fork
}

up() {
    cd $PROJECT_PATH || exit_status 1
    source .venv/bin/activate
    git pull
    sudo systemctl restart $PROJECT_NAME
    sudo systemctl status $PROJECT_NAME
}

help() {
    echo "Usage: $0 [init|init-pyenv|init-submodule|init-service|run-mongodb|run|up|help]"
    echo "  init: Initialize the project."
    echo "  init-pyenv: Initialize python environment."
    echo "  init-submodule: Initialize git submodule."
    echo "  init-service: Initialize service."
    echo "  run-mongodb: Run mongodb service."
    echo "  run: Run the server."
    echo "  up: Update the project."
    echo "  help: Show this help message."
    exit 1
}

# Check python version
get_python_env
check_git
initialize_variables

case "$1" in
"init")
    init_pyenv
    init_submodule
    init_conf
    ;;
"init-pyenv")
    init_pyenv
    ;;
"init-submodule")
    init_submodule
    ;;
"init-service")
    # init_pyenv
    init_service
    ;;
"run-mongodb")
    run_mongodb
    ;;
"run")
    run
    ;;
"up")
    up
    ;;
"help")
    help
    ;;
*)
    help
    ;;
esac
