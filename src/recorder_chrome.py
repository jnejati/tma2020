import subprocess
import time
import os

def kill_app(package_name):
    adb ='/usr/bin/adb '
    #cmd = adb + "shell ps | grep " + package_name + " | awk '{print $2}' | xargs adb shell pkill "
    cmd = adb + 'shell killall -9 ' + package_name
    print(cmd)
    subprocess.call(cmd, shell=True)

with open("../config/activities.txt", "r") as browsers:
    for line in browsers:
        if line.startswith('#'):
            continue
        browser = line.split(',')[0]
        version = line.split(',')[1].replace('.','_').strip()
        print(browser)
        package_name = browser.strip().split('/')[0]
        activity_name = browser.strip().split('/')[1]
        print('Current browser: ' + browser)
        with open("../config/testsuite.txt", "r") as sites:
            for site in sites:
                if not  site.startswith('#'):
                    print('Current site: ' + site)
                    adb ='/usr/bin/adb '
                    app_id = '"' + 'org.mozilla.firefox.application_id_' + package_name.replace('.', '_') + '"'
                    print('app_id', app_id)
                    frag = '#'
                    mitmdump_cmd = 
                    if not site.endswith('/'):
                        frag  = '/' + frag
                        site = site.strip() + frag + version
                    launch_cmd = adb + 'shell am start -n ' + browser.strip() + ' -a ' + '"android.intent.action.VIEW"' + ' -d ' + site + ' --es ' + app_id  +  ' "'  + package_name + '"'
                    print('Current launch_cmd: ' + str(launch_cmd))
                    subprocess.call(launch_cmd, shell=True)
                    time.sleep(35)
                    kill_app(package_name) 
