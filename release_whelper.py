import os
import shutil
import whelper
import argparse


def get_conda_envs_names(envs_dir):
    # Get the path to the Anaconda environments directory

    # List all directories in the environments directory
    env_dirs = os.listdir(envs_dir)

    # Filter out non-environment directories
    env_names = [env for env in env_dirs if os.path.isdir(os.path.join(envs_dir, env))]

    return env_names


def get_python_version(env_path):
    python_path = os.path.join(env_path, "bin", "python")
    version_output = os.popen(f"{python_path} --version").read()
    version = version_output.strip().split()[1].split(".")[:2]
    return ".".join(version)


def copy_whelper_to_envs(envs_dir, envs, whelper_path, override_all, test_env=False):
    def write_whelper_to_env(env, python_version, whelper_path, dest_path):
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

        shutil.copytree(
            whelper_path,
            dest_path,
            ignore=shutil.ignore_patterns(".*"),
        )
        print(f"whelper.py copied to {env} environment (Python {python_version}).")

    if test_env:
        envs = [test_env]

    overwrite_whenever_possible_with_user_consent = override_all

    for env in envs:
        env_path = os.path.join(envs_dir, env)
        python_version = get_python_version(env_path)
        dest_path = os.path.join(
            env_path, "lib", f"python{python_version}", MODULE_NAME
        )

        if (
            os.path.exists(dest_path)
            and not overwrite_whenever_possible_with_user_consent
        ):
            user_overwrite_choice = input(
                f"{dest_path} is already existed.\nDo you want to overwrite it? (y/[n]/all): "
            )
            while user_overwrite_choice not in ["y", "n", "all", "diff"]:
                user_overwrite_choice = input(
                    f"Do you want to overwrite it? (y/[n]/all): "
                )
            match user_overwrite_choice:
                case "y":
                    write_whelper_to_env(env, python_version, whelper_path, dest_path)
                case "n":
                    print(f"Skip overwriting whelper in {env}")
                case "all":
                    print(f"Overwriting whelper in remaining envs whenver possible.")
                    write_whelper_to_env(env, python_version, whelper_path, dest_path)
                    overwrite_whenever_possible_with_user_consent = True

        else:
            write_whelper_to_env(env, python_version, whelper_path, dest_path)


if __name__ == "__main__":
    ENVS_DIR = os.path.expanduser("~/opt/miniconda3/envs")
    PWD = whelper.dirname(__file__)
    MODULE_NAME = "whelper"

    # Set up argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", required=False, action="store_true")
    args = parser.parse_args()

    # Get the conda environment names
    conda_envs_names = get_conda_envs_names(ENVS_DIR)

    # Specify the path to whelper.py
    whelper_path = os.path.join(PWD)

    # Copy whelper.py to all Conda environments
    copy_whelper_to_envs(
        ENVS_DIR, conda_envs_names, whelper_path, override_all=args.all
    )

    # CR-someday: Code for unit testing, will be moved to testing file later
    # copy_whelper_to_envs(
    #     ENVS_DIR, conda_envs_names, whelper_path, test_env="standard-gui"
    # )
