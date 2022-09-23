import os
import sys
import argparse
import subprocess
from jupyter_server.serverapp import list_running_servers
import shutil
import time
import yaml
from tabulate import tabulate
from hk_utils import print

config = None
workspaces = {}
unavailable_workspace_names = set()

def load_config(config_path="~/.jlmanager/config.yaml"):
    global config

    # set default config
    config = {
        "conda_path": "~/miniconda3",
        "workspace_path": "~/workspace",
        "default_python": "3.10",
        "default_ip": "127.0.0.1",
        "default_port": "8888",
        "operation_waiting_timeout": 10,
    }

    # load config
    config_path = os.path.expanduser(config_path)
    if os.path.exists(config_path):
        with open(config_path) as f:
            config.update(yaml.safe_load(f))

    # expand user paths
    for key in ["conda_path", "workspace_path"]:
        config[key] = os.path.expanduser(config[key])

    return config

def update_workspaces():
    workspaces.clear()
    unavailable_workspace_names.clear()
    
    workspace_names_in_conda_dir = set(os.listdir(f"{config['conda_path']}/envs"))
    workspace_names_in_workspace_dir = set(os.listdir(f"{config['workspace_path']}"))

    workspace_names = workspace_names_in_conda_dir & workspace_names_in_workspace_dir
    unavailable_workspace_names.update(workspace_names_in_conda_dir | workspace_names_in_workspace_dir)
    
    all_running_servers = {}
    for item in list(list_running_servers()):
        workspace_name = os.path.basename(item["root_dir"])
        if workspace_name not in all_running_servers:
            all_running_servers[workspace_name] = []
        
        all_running_servers[workspace_name].append({
            "ip": item["hostname"],
            "port": item["port"],
            "pid": item["pid"],
            "token": item["token"],
            "url": item["url"] + f"lab?token={item['token']}",
        })

    for workspace in workspace_names:
        workspace_dir = os.path.join(config["workspace_path"], workspace)

        # check if .jlab exist in the workspace directory
        if not os.path.exists(os.path.join(workspace_dir, ".jlab")):
            continue
        
        python_path = os.path.join(config["conda_path"], "envs", workspace, "bin", "python")
        python_ver = ".".join(subprocess.check_output([python_path, "--version"]).decode("utf-8").strip().split(" ")[1].split(".")[:2])

        # check if jupyterlab is installed
        if not os.path.exists(os.path.join(config["conda_path"], "envs", workspace, "lib", f"python{python_ver}", "site-packages", "jupyterlab")):
            continue

        running_servers = None if workspace not in all_running_servers else sorted(all_running_servers[workspace], key=lambda x: x["port"])

        workspaces[workspace] = {
            "directory": workspace_dir,
            "python": python_ver,
            "running": running_servers,
        }

    return workspaces

def delete_workspace(workspace_name):
    # remove workspace directory
    shutil.rmtree(workspaces[workspace_name]["directory"], ignore_errors=True)

    # remove conda environment
    subprocess.run(
        f"{os.path.join(config['conda_path'], 'condabin', 'conda')} env remove -n {workspace_name}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
    )
    
    print.success(f"Workspace \"{workspace_name}\" deleted.")

def parse_arg(argv):
    parser = argparse.ArgumentParser(description="Jupyterlab Workspace Manager")
    subparsers = parser.add_subparsers()

    # create
    parser_create = subparsers.add_parser("create", help="Create a new workspace")
    parser_create.add_argument("workspace_name", help="Name of the workspace to create")
    parser_create.add_argument("-f", "--force", action="store_true", help="If the workspace already exists, overwrite it")
    parser_create.add_argument("--python", default=config["default_python"], help="Python version to use")
    parser_create.set_defaults(func=do_create)

    # list
    parser_list = subparsers.add_parser("list", help="List workspaces")
    parser_list.add_argument("-r", "--running", action="store_true", help="Only list running workspaces")
    parser_list.add_argument("-R", "--not-running", action="store_true", help="Only list not running workspaces")
    parser_list.add_argument("-v", "--verbose", action="store_true", help="Show details")
    parser_list.set_defaults(func=do_list)

    # start
    parser_start = subparsers.add_parser("start", aliases=["run"], help="Start a workspace")
    parser_start.add_argument("workspace_name", help="Name of the workspace to start")
    parser_start.set_defaults(func=do_start)

    # stop
    parser_stop = subparsers.add_parser("stop", aliases=["kill"], help="Stop a workspace")
    parser_stop.add_argument("workspace_name", help="Name of the workspace to stop")
    parser_stop.set_defaults(func=do_stop)

    # delete
    parser_delete = subparsers.add_parser("delete", help="Delete a workspace")
    parser_delete.add_argument("workspace_name", help="Name of the workspace to delete")
    parser_delete.set_defaults(func=do_delete)

    if len(argv) == 1:  # if no arguments are provided, show help
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:  # run parsing
        args = parser.parse_args()
        args.func(args)

def do_create(args):
    update_workspaces()

    workspace_name = args.workspace_name
    workspace_path = os.path.join(config["workspace_path"], workspace_name)
    python_version = args.python
    is_force = args.force

    # check if workspace already exists
    if workspace_name in unavailable_workspace_names:
        if is_force:
            print.warning(f"Workspace name \"{workspace_name}\" already occupied. Overwriting...")
            delete_workspace(workspace_name)
        else:
            print.error(f"Workspace name \"{workspace_name}\" already occupied. Abort.")
            return
    
    # create conda environment
    subprocess.run(
        f"{os.path.join(config['conda_path'], 'condabin', 'conda')} create -y -n {workspace_name} python={python_version} jupyterlab",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
    )

    # create workspace directory
    os.makedirs(workspace_path, exist_ok=True)

    # create jupyterlab config file
    with open(f"{workspace_path}/.jlab_config.py", "w") as f:
        f.write(f"c.ServerApp.ip = '{config['default_ip']}'\n")
        f.write(f"c.ServerApp.port = {config['default_port']}\n")
        f.write(f"c.ServerApp.open_browser = False\n")
    
    # create jupyterlab execution file
    with open(f"{workspace_path}/.jlab", "w") as f: 
        f.write('eval "$(conda shell.bash hook)"\n')
        f.write(f'conda activate {workspace_name}\n')
        f.write('\n')
        f.write('cd "$(dirname "$0")"\n')
        f.write('\n')
        f.write('jupyter lab --config=".jlab_config.py"\n')

    # make jupyterlab execution file executable
    os.chmod(f"{os.path.join(workspace_path, '.jlab')}", 0o755)

    print.success(f"Workspace \"{workspace_name}\" created.")

def do_list(args):
    update_workspaces()

    is_running = args.running
    is_not_running = args.not_running
    is_verbose = args.verbose

    if is_running:
        if is_verbose:
            rows = []
            for workspace_name, workspace_info in workspaces.items():
                if workspace_info["running"] is None:
                    continue
                for running_server_info in workspace_info["running"]:
                    rows.append([
                        workspace_name,
                        workspace_info["directory"],
                        workspace_info["python"],
                        running_server_info["pid"],
                        running_server_info["url"]
                    ])

            print(tabulate(rows, headers=["Workspace", "Directory", "Python", "PID", "URL"]))
        else:
            print('\n'.join([workspace_name for workspace_name, workspace_info in workspaces.items() if workspace_info["running"]]))
    elif is_not_running:
        if is_verbose:
            rows = []
            for workspace_name, workspace_info in workspaces.items():
                if workspace_info["running"] is not None:
                    continue
                rows.append([
                    workspace_name,
                    workspace_info["directory"],
                    workspace_info["python"],
                ])

            print(tabulate(rows, headers=["Workspace", "Directory", "Python"]))
        else:
            print('\n'.join([workspace_name for workspace_name, workspace_info in workspaces.items() if not workspace_info["running"]]))
    else:
        if is_verbose:
            rows = [[
                workspace_name,
                workspace_info["directory"],
                workspace_info["python"],
                "*" if workspace_info["running"] else ""
            ] for workspace_name, workspace_info in workspaces.items()]
            
            # Note
            #  colalign has bug : when rows are empty, it generates error
            if len(rows) == 0:
                print(tabulate(
                    rows,
                    headers=["Workspace", "directory", "python", "running"]
                ))
            else:
                print(tabulate(
                    rows,
                    headers=["Workspace", "directory", "python", "running"],
                    colalign=("left", "left", "right", "center")
                ))
        else:
            print('\n'.join(workspaces.keys()))

def do_start(args):
    update_workspaces()

    workspace_name = args.workspace_name

    if workspace_name not in workspaces:
        print.error(f"Workspace \"{workspace_name}\" does not exist. Abort.")
        return

    if workspaces[workspace_name]["running"]:
        print.warning(f"Workspace \"{workspace_name}\" is already running.")
        for running_server_info in workspaces[workspace_name]["running"]:
            print.info(f"URL: {running_server_info['url']}")
            
        return

    with open(os.path.join(workspaces[workspace_name]["directory"], ".jlab.log"), "w") as f:
        subprocess.Popen(
            ['nohup', f"{os.path.join(config['workspace_path'], workspace_name, '.jlab')}"],
            stdout=f,
            stderr=f,
            preexec_fn=os.setpgrp()
        )

    waiting_start_time = time.time()
    while time.time() - waiting_start_time < config["operation_waiting_timeout"]:
        update_workspaces()
        if workspaces[workspace_name]["running"]:
            print.success(f"Workspace \"{workspace_name}\" started.")
            for running_server_info in workspaces[workspace_name]["running"]:
                print.info(f"URL: {running_server_info['url']}")
            return
        time.sleep(1)
    
    print.error(f"Workspace \"{workspace_name}\" failed to start. Abort.")

def do_stop(args):
    update_workspaces()
    workspace_name = args.workspace_name

    if workspace_name not in workspaces:
        print.error(f"Workspace \"{workspace_name}\" does not exist. Abort.")
        return
    
    if not workspaces[workspace_name]["running"]:
        print.warning(f"Workspace \"{workspace_name}\" is not running.")
        return
    
    for running_server in workspaces[workspace_name]["running"]:
        subprocess.run(
            f"kill {running_server['pid']}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        print.success(f"Workspace \"{workspace_name}\" stopped({running_server['pid']}).")

def do_delete(args):
    update_workspaces()

    workspace_name = args.workspace_name

    if workspace_name not in workspaces:
        print.error(f"Workspace \"{workspace_name}\" does not exist. Abort.")
        return

    if workspaces[workspace_name]["running"]:
        print.warning(f"Workspace \"{workspace_name}\" is running. Stopping...")
        do_stop(args)
    
    delete_workspace(workspace_name)

if __name__ == '__main__':
    load_config()
    parse_arg(sys.argv)
