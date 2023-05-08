import os
import getpass
import re
import sys
import argparse
import subprocess
from hk_libs import print

__version__ = "1.2.4"

class ConfigParser:
    def __init__(self):
        self._default = { "User": getpass.getuser(), "Port": '22' }
        self._comment_symbol = "#"
        self._annotation_symbol = "@"
    
    def _is_comment(self, line):
        return line.lstrip().startswith(self._comment_symbol)

    def _is_annotation(self, line):
        return line.lstrip().startswith(self._annotation_symbol)

    def _is_emptyline(self, line):
        return len(line.strip()) == 0

    def _key(self, line):
        return line.split(":")[0].strip()

    def _value(self, line):
        return ":".join(line.split(":")[1:]).strip()

    def _indent(self, line):
        return len(line) - len(line.lstrip())

    def _parse(self, lines):
        for line_idx in [i for i, line in enumerate(lines) if self._key(line) == "default"]:
            i = line_idx + 1
            while i < len(lines) and self._indent(lines[i]) > 0:
                self._default[self._key(lines[i])] = self._value(lines[i])
                i += 1

        config = {}

        for line_idx in [i for i, line in enumerate(lines) if self._key(line) == "Host"]:
            hosts = self._value(lines[line_idx]).split(" ")

            # annotations
            host_annotations = []
            i = line_idx - 1
            while i > 0 and self._indent(lines[i]) == 0 and self._is_annotation(lines[i]):
                host_annotations.append(lines[i].strip())
                i -= 1

            # options
            if "@useDefault" in host_annotations:
                options = self._default.copy()
            else:
                options = {}
            
            i = line_idx + 1
            while i < len(lines) and self._indent(lines[i]) > 0:
                options[self._key(lines[i])] = self._value(lines[i])
                i += 1
            
            for host in hosts:
                if host not in config:
                    config[host] = {}
                
                config[host].update(options)
        
        # parse interpolations
        for host in config:
            options = config[host].copy()
            options["Host"] = host
            locals().update(options)

            for key in config[host]:
                value = config[host][key]
                interpolations = re.findall(r"\{\{ *(.*?) *\}\}", value)
                for interpolation in interpolations:
                    config[host][key] = re.sub(r"\{\{ *(.*?) *\}\}", eval(interpolation), value)
        
        return config

    def load(self, config_file):
        config_file = os.path.expanduser(config_file)
        if not os.path.exists(config_file):
            return None
        
        with open(config_file, "r") as f:
            lines = [
                line.rstrip() for line in f.readlines()
                if not self._is_comment(line) and not self._is_emptyline(line)
            ]
        
        return self._parse(lines)

config_parser = ConfigParser()

def parse_arg(argv):
    parser = argparse.ArgumentParser(description="assh : Advanced SSH")

    subparsers = parser.add_subparsers()

    # list
    parser_list = subparsers.add_parser("list", aliases=["l"], help="list all hosts")
    parser_list.add_argument("-f", "--config-file", help="specify the config file. If not specified, ~/.ssh/assh.config is used.", default="~/.ssh/assh.config")
    parser_list.set_defaults(func=do_list)

    # connect
    parser_connect = subparsers.add_parser("connect", aliases=["c"], help="connect to a host")
    parser_connect.add_argument("-f", "--config-file", help="specify the config file. If not specified, ~/.ssh/assh.config is used.", default="~/.ssh/assh.config")
    parser_connect.add_argument("host", help="host to connect to. Can only use host in the config file.")
    parser_connect.add_argument("ssh_options", nargs=argparse.REMAINDER, help="additional ssh options")
    parser_connect.set_defaults(func=do_connect)

    # update ssh config file
    parser_update_ssh_config_file = subparsers.add_parser("update-ssh", aliases=["u"], help="update the SSH config file")
    parser_update_ssh_config_file.add_argument("-f", "--config-file", help="specify the config file. If not specified, ~/.ssh/assh.config is used.", default="~/.ssh/assh.config")
    parser_update_ssh_config_file.add_argument("--overwrite", help="overwrite the SSH config file if it exists. The existed file will be backuped to ~/.ssh/config.old", action="store_true")
    parser_update_ssh_config_file.set_defaults(func=do_update_ssh)

    # version
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    if len(argv) == 1:  # if no arguments are provided, show help
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:  # run parsing
        args = parser.parse_args()
        args.func(args)

def do_list(args):
    config = config_parser.load(args.config_file)
    if config is None:
        print.error("No assh config file found.")
        sys.exit(1)

    print("\n".join(config.keys()))

def do_connect(args):
    config = config_parser.load(args.config_file)
    if config is None:
        print.error("No assh config file found.")
        sys.exit(1)

    host = args.host.split(".")[0]
    dot_options = args.host.split(".")[1:]

    if host not in config:
        print.error(f"host not found: {host}")
        sys.exit(1)
    elif not set(["User", "HostName", "Port", "IdentityFile"]).issubset(set(config[host].keys())):
        print.error(f"invalid config: {host}")
        sys.exit(1)
    
    cmdline = f"ssh -p {config[host]['Port']}"

    if "IdentityFile" in config[host]:
        cmdline += f" -i {config[host]['IdentityFile']}"

    if "LocalFowrad" in config[host]:
        cmdline += f" -L {config[host]['LocalFowrad'.replace(' ', ':')]}"

    for local_forward_port in [item[1:] for item in dot_options if item.startswith("L")]:
        cmdline += f" -L {local_forward_port}:localhost:{local_forward_port}"
    
    for key in [key for key in config[host] if key not in ["User", "HostName", "Port", "IdentityFile"]]:
        cmdline += f" -o {key}={config[host][key]}"

    cmdline += f" {config[host]['User']}@{config[host]['HostName']}"

    subprocess.run(cmdline, shell=True)
    print.info("connection terminated")

def do_update_ssh(args):
    config = config_parser.load(args.config_file)
    if config is None:
        print.error("No assh config file found.")
        sys.exit(1)

    is_overwrite = args.overwrite
    ssh_config_file = os.path.expanduser("~/.ssh/config")
    if os.path.exists(ssh_config_file):
        if is_overwrite:
            old_ssh_config_file = os.path.join(os.path.dirname(ssh_config_file), f"{ssh_config_file}.old")
            print.warning(f"SSH config file already exists. Overwrite it(old SSH config file at {old_ssh_config_file}).")
            os.rename(ssh_config_file, old_ssh_config_file)
        else:
            print.error("SSH config file already exists. Use --overwrite to overwrite it.")
            sys.exit(1)
    
    with open(ssh_config_file, "w") as f:
        for host in config:
            f.write(f"Host {host}\n")
            for key in config[host]:
                f.write(f"    {key} {config[host][key]}\n")
            f.write("\n")

if __name__ == "__main__":
    parse_arg(sys.argv)




