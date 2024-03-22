import colorama
import pathlib
import os
import ipaddress
import secrets
import sys

PROJECT_NAME = "lexinavigator"
PROJECT_PATH = pathlib.Path(__file__).parent.parent.resolve()
TOOLS_PATH = pathlib.Path(__file__).parent.resolve()
ENV_BIN_DIR = pathlib.Path(PROJECT_PATH, ".venv/bin").resolve()

DEFAULT_APP_DATA_PATH = pathlib.Path(PROJECT_PATH, "app_data").resolve()
DEFAULT_CONFIG_PATH = pathlib.Path(DEFAULT_APP_DATA_PATH, "config").resolve()
DEFAULT_LOG_PATH = pathlib.Path(DEFAULT_APP_DATA_PATH, "logs").resolve()

CONFIG_TEMPLATE_PATH = pathlib.Path(TOOLS_PATH, "config_templates").resolve()


def get_template_outout_path(template_name, output_path, rename=""):
    outname = rename or pathlib.Path(template_name).stem
    template_path = pathlib.Path(CONFIG_TEMPLATE_PATH, template_name).resolve()
    outpath = pathlib.Path(output_path, outname).resolve()
    return template_path, outpath


DEFAULT_ENV_FILE_TEMPLATE, DEFAULT_ENV_FILE = get_template_outout_path(
    "env.template", PROJECT_PATH, rename=".env-release")

DEFAULT_SERVICE_TEMPLATE, DEFAULT_SERVICE_FILE = get_template_outout_path(
    "service.template", "/etc/systemd/system/", rename=f"{PROJECT_NAME}.service")

DEFAULT_UVICORN_TEMPLATE, DEFAULT_UVICORN_CONF = get_template_outout_path(
    "uvicorn_conf.py.template", DEFAULT_CONFIG_PATH)


colorama.init(autoreset=True)


def write_to_file(file_path, content):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(file_path, "w") as f:
        f.write(content)


def prompt_yes_or_no(prompt):
    while True:
        response = input(
            f"{colorama.Fore.YELLOW}{prompt} {colorama.Fore.GREEN}(y/n)  ").lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print(
                f"{colorama.Style.BRIGHT+colorama.Fore.RED}Invalid answer."
                f"Please quesion {colorama.Fore.GREEN}'y' {colorama.Fore.RED}or {colorama.Fore.GREEN}'n'.")
            continue


def init_uvicorn_conf():
    if pathlib.Path(DEFAULT_UVICORN_CONF).exists():
        if not prompt_yes_or_no(
            f"{colorama.Fore.YELLOW}{colorama.Fore.GREEN}{DEFAULT_UVICORN_CONF}{colorama.Fore.YELLOW} already exists. Do you want to overwrite it?"
        ):
            return

    with open(DEFAULT_UVICORN_TEMPLATE, "r") as f:
        content = f.read()

    while True:
        ipaddr = input(
            f"{colorama.Fore.YELLOW}Bin IP (default 127.0.0.1:8000): ")
        if not ipaddr:
            ip = "127.0.0.1"
            port = 8000
            break
        # check ip addr
        try:
            ip, port = ipaddr.split(":")
            ipaddress.ip_address(ip)
            port = int(port)
            if port < 0 or port > 65535:
                raise ValueError
            break
        except ValueError:
            print(f"{colorama.Style.BRIGHT+colorama.Fore.RED}Invalid IP address.")
            continue
    content = content.replace("{{HOST}}", ip)
    content = content.replace("{{PORT}}", str(port))

    write_to_file(DEFAULT_UVICORN_CONF, content)


def init_env_conf():
    if pathlib.Path(DEFAULT_ENV_FILE).exists():
        if not prompt_yes_or_no(
            f"{colorama.Fore.YELLOW}{DEFAULT_ENV_FILE} already exists. Do you want to overwrite it?"
        ):
            return

    with open(DEFAULT_ENV_FILE_TEMPLATE, "r") as f:
        content = f.read()

    content = content.replace("{{APP_NAME}}", PROJECT_NAME)
    content = content.replace("{{SECRET_KEY}}", secrets.token_hex(32))
    content = content.replace("{{SIGNUP_SECRET_KEY}}", secrets.token_hex(32))
    content = content.replace("{{APP_DATA_PATH}}", str(DEFAULT_APP_DATA_PATH))

    write_to_file(DEFAULT_ENV_FILE, content)


def init_nginx_conf():
    nginx_config_dir = input(
        f"{colorama.Fore.YELLOW}Nginx config path(default: {colorama.Fore.GREEN}/etc/nginx): ")
    nginx_config_dir = nginx_config_dir or "/etc/nginx"
    if not os.path.isdir(nginx_config_dir):
        print(f"{colorama.Fore.RED}Nginx not support!!!")
        return
    if not os.path.isfile(os.path.join(nginx_config_dir, "nginx.conf")):
        print(f"{colorama.Fore.RED}Nginx not installed!!!")
        return

    if pathlib.Path(nginx_config_dir).exists():
        if not prompt_yes_or_no(
            f"{colorama.Fore.YELLOW}{nginx_config_dir} already exists. Do you want to overwrite it?"
        ):
            return

    if os.path.isdir(os.path.join(nginx_config_dir, "sites-available")):
        nginx_config_file = os.path.join(
            nginx_config_dir, "sites-available", f"{PROJECT_NAME}.conf")
    elif os.path.isdir(os.path.join(nginx_config_dir, "conf.d")):
        nginx_config_file = os.path.join(
            nginx_config_dir, "conf.d", f"{PROJECT_NAME}.conf")
    else:
        print(f"{colorama.Fore.RED}Nginx config path not found!!!")
        return

    domain = input(
        f"{colorama.Fore.YELLOW}Enter the domain name or ip (default {colorama.Fore.GREEN}: 127.0.0.1): ")

    port = input(
        f"{colorama.Fore.YELLOW}Enter the port (default {colorama.Fore.GREEN}: 8888): ")

    local_server_ip = input(
        f"{colorama.Fore.YELLOW}Enter the local server ip"
        f" and port (default {colorama.Fore.GREEN}: http://127.0.0.1:8000): ")

    template_file = get_template_outout_path("nginx.conf.template", "")
    with open(template_file, "r") as f:
        content = f.read()

    content = content.replace("{{PUBLIC_IP}}", domain)
    content = content.replace("{{PORT}}", port)
    content = content.replace("{{LOCAL_IP}}", local_server_ip)

    print(
        f"Run {colorama.Fore.RED}sudo systemctl reload nginx{colorama.Fore.RESET} to apply changes.")
    print(
        f"Additional modifications are in the file: {colorama.Fore.GREEN}{nginx_config_file}")


def init_service_conf():
    import pwd
    import grp
    uid = os.getuid()
    userinfo = pwd.getpwuid(uid)
    group_info = grp.getgrgid(userinfo.pw_gid)
    user_name = userinfo.pw_name
    group_name = group_info.gr_name

    if pathlib.Path(DEFAULT_SERVICE_FILE).exists():
        if not prompt_yes_or_no(
            f"{colorama.Fore.YELLOW}{DEFAULT_SERVICE_FILE} already exists. Do you want to overwrite it?"
        ):
            return

    with open(DEFAULT_SERVICE_TEMPLATE, "r") as f:
        content = f.read()

    content = content.replace("{{USER}}", user_name)
    content = content.replace("{{GROUP}}", group_name)
    content = content.replace("{{WORKING_DIR}}", str(PROJECT_PATH))
    content = content.replace("{{ENV_BIN_DIR}}", str(ENV_BIN_DIR))
    content = content.replace(
        "{{RUN_SCRIPT}}", f"{ENV_BIN_DIR}/python {PROJECT_PATH}/run.py")
    content = content.replace("{{LOG_FILE}}", str(
        DEFAULT_LOG_PATH / "access.log"))
    content = content.replace("{{ERROR_LOG_FILE}}",
                              str(DEFAULT_LOG_PATH / "error.log"))
    content = content.replace("{{OPTIONS}}", "")

    write_to_file(DEFAULT_SERVICE_FILE, content)


def init_default_app_data_dir():
    if not DEFAULT_APP_DATA_PATH.exists():
        DEFAULT_APP_DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_CONFIG_PATH.exists():
        DEFAULT_CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_LOG_PATH.exists():
        DEFAULT_LOG_PATH.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "init-conf":
        init_env_conf()
        init_uvicorn_conf()
        init_default_app_data_dir()
    elif cmd == "init-nginx":
        init_nginx_conf()
    elif cmd == "init-service":
        init_service_conf()
    else:
        print(f"help: {sys.argv[0]} init-conf|init-nginx|init-service")
