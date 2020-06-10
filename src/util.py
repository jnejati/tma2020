import subprocess
import time

def kill_app(package_name):
    adb ='/usr/bin/adb '
    cmd = adb + "shell ps | grep " + package_name + " | awk '{print $2}' | xargs adb shell kill "
    #cmd = adb + 'shell killall -9 ' + package_name
    #cmd = adb + 'shell pkill ' + package_name
    print(cmd)
    subprocess.call(cmd, shell=True)
    time.sleep(2)

def tc():
    cmd = '/home/jnejati/bperf/src/init.sh' 
    subprocess.call(cmd, shell=True)
