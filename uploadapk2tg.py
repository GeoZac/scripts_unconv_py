#!/usr/bin/env python3

import asyncio
import sys
from datetime import datetime as dt
from glob import glob
from json import load
from os import getcwd, getenv, path

from git import Repo
from git.exc import InvalidGitRepositoryError
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import NetworkError
from telegram.helpers import escape_markdown


def set_path():
    # Get the directory where script is run from, required for project name
    if len(sys.argv) > 1:
        passed_path = sys.argv[1]
        if path.isabs(passed_path):
            return passed_path
        return "".join([getcwd(), "\\", passed_path])
    return getcwd()


def get_repo_info(dir_path):
    try:
        repo = Repo(path=dir_path)
        return repo
    except InvalidGitRepositoryError:
        return None


async def upload_via_bot(
    bot_token,
    chat_id,
    msg_content,
    apk_file,
    project_name,
    version_name,
):
    # Init the Bot
    bot = Bot(token=bot_token)

    try:
        # Send the info message
        await bot.sendMessage(
            chat_id=chat_id,
            text=f"{msg_content}",
            disable_notification=False,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except NetworkError:
        pass

    # Rename to avoid generic artficat name
    file_name = path.split(apk_file)[-1].replace("app", project_name)

    # Upload the file
    with open(apk_file, "rb") as sent_file:
        try:
            await bot.sendDocument(
                filename=file_name,
                chat_id=chat_id,
                document=sent_file,
                caption=escape_markdown(
                    f"#{project_name} {version_name}", version=2, entity_type="CODE"
                ),
                disable_notification=False,
                parse_mode=ParseMode.MARKDOWN_V2,
                timeout=2000,
            )
        except NetworkError as e:
            print(e.with_traceback)
            print(e.message)
            # pass


def get_branch_info(git_dir):
    git_repo = get_repo_info(git_dir)
    if not git_repo:
        return None
    return str(git_repo.head.ref)


def parse_json_info(metadata_file):
    with open(metadata_file) as json_file:
        output_data = load(json_file)
        try:
            elements = output_data["elements"][0]
            version_name = elements["versionName"]
            version_code = elements["versionCode"]
            variant_type = output_data["variantName"]
        except TypeError:
            # For compatibility with Android gradle plugin < v4.0.0
            print("Oops, old format")
            apk_data = output_data[0]["apkData"]
            version_name = apk_data["versionName"]
            version_code = apk_data["versionCode"]
            variant_type = ""
        return version_name, version_code, variant_type


def gather_file_info(directory):
    # Some projects now builds AAB, in that case we need to figure what to do next
    aab_files = glob(f"{directory}/**/*.aab", recursive=True)
    if aab_files:
        if (
            input(
                "Found App Bundle in project, Needs manual intervention\n"
                "Or continue with apk upload?"
            )
            != "y"
        ):
            sys.exit(0)

    # Get the APK files available
    apk_files = glob(f"{directory}/**/*.apk", recursive=True)
    apk_files.sort(key=path.getmtime, reverse=True)

    # If the APK file doesn't exist, we need not do anything
    if not apk_files:
        print(
            "An apk build doesn't seem to be generated in the current directory or subdirectories"
        )
        sys.exit(0)

    # Successful Gradle build leaves a json file with "output" in the filename, parse it to get the version name
    json_files = glob(f"{directory}/**/output*.json", recursive=True)
    json_files.sort(key=path.getmtime, reverse=True)

    # If the JSON file doesn't exist, we need not do anything either
    if not json_files:
        print("Directory doesn't seem to be Android Project")
        sys.exit(0)

    return apk_files[0], json_files[0]


def build_commit_log(git_dir):
    commit_log = ""
    git_repo = get_repo_info(git_dir)
    if not git_repo:
        return None
    build_branch = str(git_repo.head.ref)
    today_date = dt.today()
    # Get last 25 commits and only add ones authored within 7 days
    for commit in list(git_repo.iter_commits(build_branch, max_count=25)):
        if (today_date - commit.authored_datetime.replace(tzinfo=None)).days > 7:
            continue
        # Adding the line-break for Commits:\nCommit#1
        # Also no need of full commit message
        commit_log += "\n· " + commit.message.split("\n")[0]
    return commit_log


def upload_apk_to_tg(current_dir):
    project_name = path.basename(current_dir)

    print("Starting apk upload script")

    apk_file, apk_info = gather_file_info(current_dir)

    version_name, version_code, variant_type = parse_json_info(apk_info)

    build_time = dt.fromtimestamp(
        path.getmtime(
            apk_file,
        ),
    ).strftime(
        "%H:%M %d/%m",
    )

    file_size = round(
        path.getsize(
            apk_file,
        )
        / (1024 * 1024),
        ndigits=2,
    )

    # Fail if file is bigger than 50MB
    if file_size > 50:
        print("File exceeds Telegram's limit")
        sys.exit

    commit_hist = build_commit_log(current_dir)
    msg_content = (
        f"Uploading compiled app\n"
        f"`Project      : {project_name}`\n"
        f"`Version Name : {version_name}`\n"
        f"`Version Code : {version_code}`\n"
        f"`Build Variant: {variant_type}`\n"
        f"`Build Time   : {build_time}`\n"
        f"`Build size   : {file_size} MB`\n"
        f"`Build Branch : {get_branch_info(current_dir)}`"
    )

    # Skip commits if the logs are empty
    if commit_hist:
        msg_content += f"\nCommits      :`{commit_hist}`"

    # Spit out the message to the console
    print(msg_content.replace("`", ""))

    return msg_content, apk_file, project_name, version_name


async def main():
    bot_token = getenv("APK_BOT_TOKEN", None)
    cid_token = getenv("APK_TGCHAT_ID", None)
    if bot_token is None or cid_token is None:
        print(
            "Missing essential environment variables\n"
            "Please set APK_BOT_TOKEN with TG Bot token\n"
            "Please set APK_TGCHAT_ID with the Channel/Group ID"
        )
        return
    current_dir = set_path()
    msg_content, apk_file, project_name, version_name = upload_apk_to_tg(current_dir)
    await upload_via_bot(
        bot_token,
        cid_token,
        msg_content,
        apk_file,
        project_name,
        version_name,
    )


if __name__ == "__main__":
    asyncio.run(
        main(),
    )
