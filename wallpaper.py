import os
import sys
import time
import subprocess
import shutil
import random
import array
from PIL import Image
import numpy as np


def setWallpaper(path, tmp_path, new_height):
    tmp_path_jpg = tmp_path.split(".")[0]+".jpg"
    
    print("Setting wallpaper to "+path, "(",tmp_path_jpg,")")
    
    img = Image.open(path)
    ratio = img.size[0]/img.size[1]
    img = img.resize((round(new_height*ratio), new_height), Image.LANCZOS)
    
    img.save(tmp_path_jpg, 'JPEG', quality=100)
    mean_colors = np.array(img).mean(axis=(0,1))/255

    if os.path.exists(tmp_path_jpg):
        cmds = [
            ['xfconf-query','-c','xfce4-desktop','-p','/backdrop/screen0/monitorDP-2/workspace0/last-image','-s',tmp_path_jpg],
            [
                'xfconf-query','-c','xfce4-desktop','-p','/backdrop/screen0/monitorDP-2/workspace0/rgba1',
                '-t','double','-s',f"{mean_colors[0]:.4f}",'-t','double','-s',f"{mean_colors[1]:.4f}",
                '-t','double','-s',f"{mean_colors[2]:.4f}",'-t','double','-s','1'
            ]
        ]
        for cmd in cmds:
            subprocess.Popen(cmd)
    else:
        print("ERROR: file not found")

path = sys.argv[1]
wait_time = float(sys.argv[2])
running_processes = subprocess.run(
    ["ps", "aux"], capture_output=True, text=True
)
wallpaper_script_running = len([line for line in running_processes.stdout.splitlines() if "wallaper.py" in line]) > 0
if wallpaper_script_running:
    print("Killing already running wallpaper script")
    subprocess.Popen(['pkill','-f','wallpaper.py'])
print("Listing frames in "+path)
file_list = next(os.walk(path), (None, None, []))[2]
random.shuffle(file_list)
print("Running image sequence from: "+path)
print("Frames: \n"+str(file_list)+"\nTotal: "+str(len(file_list)))
output = subprocess.check_output("xrandr | grep '*' | awk '{print $1}'", shell=True)
resolution = output.decode().strip().split('x')
print(f"Screen size: {resolution}")
print("Animating")
while True:
    for file in file_list:
        file_path = path+file
        tmp_path = "/tmp/"+file_path.split('.')[0].split('/')[-1]+"_tmp"+"."+file_path.split('.')[1]
        setWallpaper(file_path, tmp_path, round(int(resolution[1])*0.8))
        time.sleep(wait_time)
        tmp_path_jpg = tmp_path.split(".")[0]+".jpg"
        os.remove(tmp_path_jpg)
