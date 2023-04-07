import subprocess
import urllib.request
import typing
import json
import tempfile
import os
import re

default_context = json.loads('''
{
    "context":{
        "client":{
            "hl":"en",
            "gl":"US",
            "deviceMake":"",
            "deviceModel":"",
            "clientName":"WEB",
            "clientVersion":"2.20230217.01.00"
        }
    }
}
''')

# URL of the script
url = "https://github.com/iv-org/youtube-utils/raw/master/scripts/yt-api-helper.sh"

temp_dir = tempfile.TemporaryDirectory()
script_path = os.path.join(temp_dir.name, "yt-api-helper.sh")
urllib.request.urlretrieve(url, script_path)
os.chmod(script_path, 0o755)

def run_yt_helper_script(*args: [str]) -> str:
        output = subprocess.run([script_path, *args], check=True, stdout=subprocess.PIPE)
        return output.stdout.decode()

def read_videos_metadata() -> typing.List[dict]:
    with open("./video/_videos.json", "r") as file:
        file_contents = file.read()
        data = json.loads(file_contents)
        return data["files"]


def write_string_to_file(filename: str, string: str):
    with open(filename, 'w') as file:
        file.write(string)


ip_replacements = [
    (r'^\s+("(clickT|t)rackingParams").+$', r'\1:""'),
    (r'[?&](sqp|rs|redir_token)=[A-Za-z0-9=-]+', ""),
    (r'(initplayback\?source=youtube)[^"]+', ""),
    (r'([&?\/]ip[=\/])[^&\/]+', "\1X.X.X.X")
]

def apply_ip_replacements(input: str) -> str:
    for (pattern, sub) in ip_replacements:
        input = re.sub(pattern, sub, input, flags=re.MULTILINE)

    return input

confirmation = input('''The generated mocks may contain your IP-Address. 
We try our best to filter it out but it may still leak. 
Do you wish to continue? (y/n): ''')

if confirmation.lower() != "y":
    print("Action cancelled.")
    exit(0)

files = read_videos_metadata()
for file in files:
    default_context.update({"videoId": file["video_id"]})
    context = json.dumps(default_context)
    video = json.loads(run_yt_helper_script("-c", "web", "-e", file['endpoint'], "--data", context))

    # Delete some useless elements
    del video['responseContext']
    if 'topbar' in video: del video['topbar']
    if 'overlay' in video: del video['overlay']
    if 'attestation' in video: del video['attestation']
    if 'frameworkUpdates' in video: del video['frameworkUpdates']


    processed_mocks = apply_ip_replacements(json.dumps(video, indent=2))
    write_string_to_file("video/"+file["name"], processed_mocks)
    


