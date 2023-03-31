import subprocess
import urllib.request
import typing
import json
import tempfile
import os

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


files = read_videos_metadata()
for file in files:
    default_context.update({"videoId": file["video_id"]})
    context = json.dumps(default_context)
    video = json.loads(run_yt_helper_script("-c", "web", "-e", file['endpoint'], "--data", context))
    del video['responseContext']
    write_string_to_file("video/"+file["name"], json.dumps(video, indent=2))
    


