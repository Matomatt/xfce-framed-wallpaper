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
    print("Setting wallpaper to "+path)

    img = Image.open(path)
    ratio = img.size[0]/img.size[1]
    img = img.resize((round(new_height*ratio), new_height))
    
    img.save(tmp_path)
    mean_colors = np.array(img).mean(axis=(0,1))/255
    print(str(mean_colors[0]),'  ',str(mean_colors[1]),'  ',str(mean_colors[2]))

    if os.path.exists(path):
        cmds = [
            ['xfconf-query','-c','xfce4-desktop','-p','/backdrop/screen0/monitorDP-2/workspace0/last-image','-s',tmp_path],
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
for file in file_list:
    file_path = path+file
    tmp_path = "/tmp/"+file_path.split('.')[0].split('/')[-1]+"_tmp"+"."+file_path.split('.')[1]
    setWallpaper(file_path, tmp_path, round(int(resolution[1])*0.8))
    time.sleep(wait_time)
    os.remove(tmp_path)
