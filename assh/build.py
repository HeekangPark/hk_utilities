import os
import glob
import shutil
import subprocess
from hk_utils import print

app_name = "assh"

def cleanup(include_tar_gz=False):
    del_list = ["build", "dist", app_name,  f"{app_name}.spec"]
    if include_tar_gz:
        del_list += glob.glob(f"{app_name}*.tar.gz")

    for item in del_list:
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item)

def get_version():
    with open(f"{app_name}.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    
    return "0.0.0"

def build(version):
    cleanup(include_tar_gz=True)
    subprocess.run(
        f"pyinstaller {app_name}.py",
        stdout=subprocess.DEVNULL,
        shell=True
    )
    subprocess.run(
        f"tar -czvf ../{app_name}-{version}.tar.gz {app_name}",
        stdout=subprocess.DEVNULL,
        shell=True,
        cwd="dist"
    )
    shutil.copy(f"{app_name}-{version}.tar.gz", f"{app_name}-latest.tar.gz")
    cleanup()

def update_scripts(version):
    with open(f"update-{app_name}.sh", "w") as f:
        f.write(f"""#!/bin/bash
            cd $HOME

            rm -rf {app_name} {app_name}-*.tar.gz
            wget https://github.com/HeekangPark/utilities/raw/master/{app_name}/{app_name}-latest.tar.gz
            tar -zxf {app_name}-latest.tar.gz
            mv {app_name}-latest {app_name}
            rm -rf {app_name}-latest.tar.gz
        """)
    
    with open(f"install-{app_name}.sh", "w") as f:
        f.write(f"""#!/bin/bash
            cd $HOME

            rm -rf {app_name} {app_name}-*.tar.gz
            wget https://github.com/HeekangPark/utilities/raw/master/{app_name}/{app_name}-latest.tar.gz
            tar -zxf {app_name}-latest.tar.gz
            mv {app_name}-latest {app_name}
            rm -rf {app_name}-latest.tar.gz

            mkdir -p scripts
            rm -f ~/scripts/{app_name}
            ln -s $HOME/{app_name}/{app_name} ~/scripts/{app_name}
            grep -qxF 'export PATH=$PATH:$HOME/scripts' ~/.bashrc || echo 'export PATH=$PATH:$HOME/scripts' >> ~/.bashrc
            source ~/.bashrc

            wget https://raw.githubusercontent.com/HeekangPark/utilities/master/{app_name}/update-{app_name}.sh
            mv update-{app_name}.sh ~/scripts
            chmod +x scripts/update-{app_name}.sh

            wget https://github.com/HeekangPark/utilities/raw/master/{app_name}/{app_name}.bash_autocompletion
            sudo chown root:root {app_name}.bash_autocompletion
            sudo mv {app_name}.bash_autocompletion /etc/bash_completion.d/{app_name}
        """)

def commit(version):
    subprocess.run(
        "git add .",
        stdout=subprocess.DEVNULL,
        shell=True
    )

    subprocess.run(
        f"git commit -m 'build {app_name}-{version}'",
        stdout=subprocess.DEVNULL,
        shell=True
    )

if __name__ == "__main__":
    version = get_version()
    build(version)
    update_scripts(version)
    commit(version)
    print.success(f"build complete : {app_name}-{version}")