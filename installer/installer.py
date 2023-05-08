import os
import sys
import json
import requests
import argparse
import subprocess

from yaspin import yaspin
from hk_libs import print

__version__ = "1.0.0"

def _convert_version_to_str(version, without_v=False):
    return ".".join(map(str, version)) if without_v else f"v{'.'.join(map(str, version))}"

def _get_latest_version_of_hk_utility(utility_name):
    url = "https://github.com/HeekangPark/hk_utilities/raw/master/versions.json"
    response = requests.get(url)
    latest = json.loads(response.text)
    return tuple(map(int, latest[utility_name].split(".")))

def _get_current_version_of_hk_utility(utility_name):
    try:
        response = subprocess.run(
            f"{utility_name} --version",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        return tuple(map(int, response.stdout.decode("utf-8").strip().split(" ")[1].split(".")))
    except:
        return (0, 0, 0) # not installed

def _check_package_installed(package_name):
    result = subprocess.run(
        f"dpkg -s {package_name}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    ).returncode

    if result == 0: # package is installed
        return True
    
    return False
    
def _install_package(package_name):
    result = subprocess.run(
        f"sudo apt install {package_name}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    ).returncode

    if result == 0:
        return True
    
    return False

def do_check_version(args):
    utility_name = args.utility_name
    
    with yaspin(text=f"checking the current version of {utility_name}...", color="cyan") as sp:
        current_version = _get_current_version_of_hk_utility(utility_name)
        sp.ok()

    if current_version == (0, 0, 0): # not installed
        print.warning(f"{utility_name} is not installed")
        return

    with yaspin(text=f"checking the latest version of {utility_name}...", color="cyan") as sp:
        latest_version = _get_latest_version_of_hk_utility(utility_name)
        sp.ok()

    if latest_version > current_version: # update available
        print.warning(f"{utility_name} needs to be updated (current: {_convert_version_to_str(current_version)}, latest: {_convert_version_to_str(latest_version)})")
    else: # up to date
        print.success(f"{utility_name} is up to date ({_convert_version_to_str(current_version)})")

def do_install(args):
    utility_name = args.utility_name
    is_force = args.force

    with yaspin(text=f"checking the current version of {utility_name}...", color="cyan") as sp:
        current_version = _get_current_version_of_hk_utility(utility_name)
        sp.ok()

    with yaspin(text=f"checking the latest version of {utility_name}...", color="cyan") as sp:
        latest_version = _get_latest_version_of_hk_utility(utility_name)
        sp.ok()

    if current_version == (0, 0, 0):
        installation_status = "not installed"
    elif latest_version > current_version:
        installation_status = "update available"
    else:
        installation_status = "up to date"

    if installation_status == "up to date" and not is_force:
        print.success(f"{utility_name} is already up to date ({_convert_version_to_str(latest_version)})")
        return
    
    should_remove_current = False
    if installation_status == "update available":
        print.warning(f"{utility_name} needs to be updated (current: {_convert_version_to_str(current_version)}, latest: {_convert_version_to_str(latest_version)})")
        should_remove_current = True
    elif installation_status == "not installed":
        print.warning(f"{utility_name} is not installed")
    else: # installation_status == "up to date" and is_force:
        print.warning(f"{utility_name} is already installed, but force option is enabled.")

    # check if wget is installed
    """
    required_packages = ["wget"]
    for package_name in required_packages:
        with yaspin(text=f"checking if {package_name} is installed...", color="cyan") as sp:
            is_installed = _check_package_installed(package_name)
            sp.ok()
        
        if is_installed:
            print.info(f"{package_name} is already installed")
        else:
            print.warning(f"{package_name} is not installed")

            with yaspin(text=f"installing {package_name}...", color="cyan") as sp:
                is_installed = _install_package(package_name)
                sp.ok()

            if is_installed:
                print.info(f"{package_name} installed")
            else:
                print.error(f"failed to install {package_name}. Abort.")
                sys.exit(1)
    """
    
    # remove current version of {app_name}
    if should_remove_current:
        with yaspin(text=f"removing current version of {utility_name}...", color="cyan") as sp:
            result = subprocess.run(
                f"rm -rf $HOME/{utility_name} $HOME/scripts/{utility_name} $HOME/.local/bash-completion/completions/{utility_name}",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            ).returncode
            sp.ok()
        
        if result != 0:
            print.error(f"failed to remove current version of {utility_name}. Abort.")
            sys.exit(1)

    # download latest version of {app_name}
    tmp_dir = "/tmp"
    filename = f"{utility_name}-{_convert_version_to_str(latest_version, without_v=True)}.tar.gz"
    filename_full = os.path.join(tmp_dir, filename)
    with yaspin(text=f"downloading latest version of {utility_name} ({_convert_version_to_str(latest_version)}) at {tmp_dir}...", color="cyan") as sp:
        result = subprocess.run(
            f"wget https://github.com/HeekangPark/hk_utilities/raw/master/{utility_name}/{filename}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=tmp_dir,
            shell=True
        ).returncode
        sp.ok()
    
    if result != 0:
        print.error(f"failed to download latest version of {utility_name}. Abort.")
        sys.exit(1)

    # extract downloaded file
    with yaspin(text=f"extracting {filename_full}...", color="cyan") as sp:
        result = subprocess.run(
            f"tar -xzf {filename}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=tmp_dir,
            shell=True
        ).returncode
        sp.ok()
    
    if result != 0:
        print.error(f"failed to extract {filename_full}. Abort.")
        sys.exit(1)
    
    # installing {app_name} : move {app_name} to home directory
    with yaspin(text=f"installing {utility_name}...", color="cyan") as sp:
        result = subprocess.run(
            f"mv {utility_name} $HOME",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=tmp_dir,
            shell=True
        ).returncode

    if result != 0:
        print.error(f"failed to install {utility_name}. Abort.")
        sys.exit(1)
        
    # cleanup
    with yaspin(text=f"cleaning up temporary files...", color="cyan") as sp:
        result = subprocess.run(
            f"rm {filename}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=tmp_dir,
            shell=True
        ).returncode
        sp.ok()
    
    if result != 0:
        print.error(f"failed to clean up temporary files. Abort.")
        sys.exit(1)

    # create ~/scripts directory if not exists
    if not os.path.exists(os.path.expandvars("$HOME/scripts")):
        with yaspin(text=f"creating ~/scripts directory...", color="cyan") as sp:
            result = subprocess.run(
                "mkdir $HOME/scripts",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            ).returncode
            sp.ok()
        
        if result != 0:
            print.error(f"failed to create ~/scripts directory. Abort.")
            sys.exit(1)

    # register ~/scripts to PATH if not registered
    paths = [os.path.expandvars(path) for path in os.environ["PATH"].split(os.pathsep)]
    if os.path.abspath(os.path.expandvars("$HOME/scripts")) not in paths:
        with yaspin(text=f"adding ~/scripts to PATH...", color="cyan") as sp:
            result = subprocess.run(
                "echo 'export PATH=$PATH:$HOME/scripts' >> $HOME/.bashrc",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            ).returncode
            sp.ok()
        
        if result != 0:
            print.error(f"failed to add ~/scripts to PATH. Abort.")
            sys.exit(1)
    
    # make {app_name} executable : create symbolic link at ~/scripts
    with yaspin(text=f"make {utility_name} executable...", color="cyan") as sp:
        result = subprocess.run(
            f"ln -s $HOME/{utility_name}/{utility_name} $HOME/scripts/{utility_name}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        ).returncode
        sp.ok()
    
    if result != 0:
        print.error(f"failed to make {utility_name} executable. Abort.")
        sys.exit(1)

    if not os.path.exists(os.path.expandvars("$HOME/.local/bash-completion/completions")):
        # download bash auto-completion
        tmp_dir = "/tmp"
        filename = f"{utility_name}.bash_autocompletion"
        with yaspin(text=f"downloading bash auto-completion for {utility_name} at {tmp_dir}...", color="cyan") as sp:
            result = subprocess.run(
                f"wget https://github.com/HeekangPark/hk_utilities/raw/master/{utility_name}/{filename}",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=tmp_dir,
                shell=True
            ).returncode
            sp.ok()
        
        if result != 0:
            print.error(f"failed to download bash auto-completion for {utility_name}. Abort.")
            sys.exit(1)

        # install bash auto-completion : move to ~/.bash_completion
        os.makedirs(os.path.expandvars("$HOME/.local/bash-completion/completions"), exist_ok=True)
        with yaspin(text=f"installing bash auto-completion for {utility_name}...", color="cyan") as sp:
            result = subprocess.run(
                f"mv {filename} $HOME/.local/bash-completion/completions/{utility_name}",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=tmp_dir,
                shell=True
            ).returncode
            sp.ok()
        
        if result != 0:
            print.error(f"failed to install bash auto-completion for {utility_name}. Abort.")
            sys.exit(1)

    print.success(f"{utility_name} is successfully installed ({_convert_version_to_str(latest_version)})")

def do_uninstall(args):
    utility_name = args.utility_name

    with yaspin(text=f"removing current version of {utility_name}...", color="cyan") as sp:
        result = subprocess.run(
            f"rm -rf $HOME/{utility_name} $HOME/scripts/{utility_name} $HOME/.local/bash-completion/completions/{utility_name}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        ).returncode
        sp.ok()
    
    if result != 0:
        print.error(f"failed to remove current version of {utility_name}. Abort.")
        sys.exit(1)
    
    print.success(f"{utility_name} is successfully uninstalled")

def parse_args(argv):
    parser = argparse.ArgumentParser(description="hk utilities installer")
    subparsers = parser.add_subparsers()

    # check_version
    parser_check_version = subparsers.add_parser("check", help="check if hk utility is up to date")
    parser_check_version.add_argument("utility_name", help="hk utility name to check")
    parser_check_version.set_defaults(func=do_check_version)

    # install
    parser_install = subparsers.add_parser("install", help="install hk utility")
    parser_install.add_argument("utility_name", help="hk utility name to install")
    parser_install.add_argument("-f", "--force", action="store_true", help="force install")
    parser_install.set_defaults(func=do_install)

    # update
    parser_update = subparsers.add_parser("update", help="update hk utility")
    parser_update.add_argument("utility_name", help="hk utility name to update")
    parser_update.add_argument("-f", "--force", action="store_true", help="force update")
    parser_update.set_defaults(func=do_install)

    # uninstall
    parser_uninstall = subparsers.add_parser("uninstall", help="uninstall hk utility")
    parser_uninstall.add_argument("utility_name", help="hk utility name to uninstall")
    parser_uninstall.set_defaults(func=do_uninstall)

    # version
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    if len(argv) == 1: # if no arguments are provided, show help
        parser.print_help(sys.stderr)
        sys.exit(1)
    else: # run parsing
        args = parser.parse_args()
        args.func(args)

if __name__ == "__main__":
    parse_args(sys.argv)

