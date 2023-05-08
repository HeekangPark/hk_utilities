import os
import glob
import json
import shutil
import subprocess
from hk_libs import print

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
        stderr=subprocess.DEVNULL,
        shell=True
    )
    subprocess.run(
        f"tar -czvf ../{app_name}-{version}.tar.gz {app_name}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
        cwd="dist"
    )
    shutil.copy(f"{app_name}-{version}.tar.gz", f"{app_name}-latest.tar.gz")

    with open("../versions.json", "r") as f:
        version_json = json.load(f)
    version_json[app_name] = version
    with open("../versions.json", "w") as f:
        json.dump(version_json, f, indent=4)

    cleanup()
    print.success(f"build complete : {app_name}-{version}")

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

    subprocess.run(
        f"git push origin master",
        stdout=subprocess.DEVNULL,
        shell=True
    )

    print.success(f"commit complete : {app_name}-{version}")

if __name__ == "__main__":
    version = get_version()
    build(version)
    commit(version)
    