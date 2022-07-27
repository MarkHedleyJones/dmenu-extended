#!/usr/bin/env python3

import argparse
import grp
import os
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install dmenu-extended systemd services"
    )
    parser.add_argument("--remove", action="store_true", help="Remove systemd services")
    parser.add_argument("--start", action="store_true", help="Start systemd services")
    parser.add_argument(
        "--rebuild-interval-mins",
        type=int,
        help="How often to update the cache (in minutes)",
    )
    return parser.parse_args()


def get_executable_path(username):
    executable_name = "dmenu_extended_cache_build"
    executable_paths = ["/usr/local/bin", "/usr/bin", f"/home/{username}/.local/bin"]
    for executable_path in executable_paths:
        path = os.path.join(executable_path, executable_name)
        if os.path.isfile(path):
            return path


def target_files(rebuild_interval_mins=20):
    username = os.environ["USER"]
    groupid = grp.getgrnam(username).gr_gid
    executable_path = get_executable_path(username)
    if not executable_path:
        raise Exception("Could not find dmenu_extended_cache_build executable")

    return {
        "dmenu-extended-update-db.service": "\n".join(
            [
                "[Unit]",
                "Description=Update dmenu-extended cache",
                "Wants=dmenu-extended-update-db.timer",
                "",
                "[Service]",
                "Type=oneshot",
                f"User={username}",
                f"Group={groupid}",
                "ExecStart=" + executable_path,
                "",
                "[Install]",
                "WantedBy=multi-user.target",
                "",
            ]
        ),
        "dmenu-extended-update-db.timer": "\n".join(
            [
                "[Unit]",
                "Description=Run update-dmenu-extended-db.service every 20 minutes",
                "Requires=dmenu-extended-update-db.service",
                "",
                "[Timer]",
                "Unit=dmenu-extended-update-db.service",
                f"OnCalendar=*:0/{rebuild_interval_mins}",
                "",
                "[Install]",
                "WantedBy=timers.target",
                "",
            ]
        ),
    }


def get_possible_install_paths():
    possible_install_paths = []
    if "XDG_CONFIG_HOME" in os.environ:
        possible_install_paths.append(os.environ["XDG_CONFIG_HOME"] + "/systemd/user")
    if "HOME" in os.environ:
        possible_install_paths.append(os.environ["HOME"] + "/.config/systemd/user")
        possible_install_paths.append(os.environ["HOME"] + "/.local/share/systemd/user")
    if "XDG_RUNTIME_DIR" in os.environ:
        possible_install_paths.append(os.environ["XDG_RUNTIME_DIR"] + "/systemd/user")
    if "XDG_DATA_HOME" in os.environ:
        possible_install_paths.append(os.environ["XDG_DATA_HOME"] + "/systemd/user")
    return possible_install_paths


def get_install_path():
    if "XDG_DATA_HOME" in os.environ:
        return os.environ["XDG_DATA_HOME"] + "/systemd/user"
    elif "HOME" in os.environ:
        return os.environ["HOME"] + "/.local/share/systemd/user"


def install(rebuild_interval_mins):
    install_path = get_install_path()
    if not os.path.isdir(install_path):
        print("Creating systemd user directory: " + install_path)
        os.makedirs(install_path)

    for filename, contents in target_files(rebuild_interval_mins).items():
        path = os.path.join(install_path, filename)
        print("Installing " + filename + " to " + install_path)
        with open(path, "w") as f:
            f.write(contents)


def run_systemd_command(user_command, silent=False):
    command = ["systemctl", "--user"] + user_command
    if silent:
        return (
            subprocess.call(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            == 0
        )
    else:
        return subprocess.call(command) == 0


def remove():
    run_systemd_command(["daemon-reload"])
    removed_files = []
    for filename in target_files().keys():
        if filename.endswith(".timer") and run_systemd_command(
            ["is-enabled", filename], silent=True
        ):
            print("Stopping " + filename + "...")
            run_systemd_command(["stop", filename])
            run_systemd_command(["disable", filename])

        for install_path in get_possible_install_paths():
            path = os.path.join(install_path, filename)
            if os.path.exists(path):
                removed_files.append(path)
                os.remove(path)
    if removed_files:
        for path in removed_files:
            print("Removed " + path)
    else:
        print("No systemd files found to remove.")


def prompt_to_start():
    print("The systemd service has been installed.")
    if input("Do you want to enable it now? [y/N] ").lower() == "y":
        run_systemd_command(["daemon-reload"])
        target = "dmenu-extended-update-db.timer"
        if run_systemd_command(["start", target]) and run_systemd_command(
            ["enable", target]
        ):
            print(f"Started {target}")


def start_service():
    run_systemd_command(["daemon-reload"])
    target = "dmenu-extended-update-db.timer"
    if run_systemd_command(["start", target]) and run_systemd_command(
        ["enable", target]
    ):
        print(f"Started {target}")


def run():
    def user_is_root():
        return os.geteuid() == 0

    args = parse_args()
    if user_is_root():
        print("This script must be run as a non-root user.")
        exit(1)
    if args.remove:
        remove()
    else:
        install(args.rebuild_interval_mins)
        if args.start or prompt_to_start():
            start_service()


if __name__ == "__main__":
    run()
