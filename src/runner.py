import subprocess
import time
import os

def kill_app(package_name):
    adb ='/usr/bin/adb '
    #cmd = adb + "shell ps | grep " + package_name + " | awk '{print $2}' | xargs adb shell pkill "
    cmd = adb + 'shell pkill -f ' + package_name
    print(cmd)
    subprocess.call(cmd, shell=True)

video_output_base_dir = '/home/jnejati/videos'
with open("../config/activities.txt", "r") as browsers:
    for line in browsers:
        browser = line.split(',')[0]
        version = line.split(',')[1].replace('.','_').strip()
        package_name = browser.strip().split('/')[0]
        activity_name = browser.strip().split('/')[1]
        print('Current browser: ' + browser)
        with open("../config/testsuite.txt", "r") as sites:
            for site in sites:
                if not  site.startswith('#'):
			print('Current site: ' + site)
			adb ='/usr/bin/adb '
                        app_id = '"' + 'com.android.browser.application_id_' + package_name.replace('.', '_') + '"'
                        print('app_id', app_id)
                        frag = '#'
                        if not site.endswith('/'):
                            frag  = '/' + frag
                        site = site.strip() + frag + version
			launch_cmd = adb + 'shell am start -n ' + browser.strip() + ' -a ' + '"android.intent.action.VIEW"' + ' -d ' + site + ' --es ' + app_id  +  ' "'  + package_name + '"'
			print('Current launch_cmd: ' + str(launch_cmd))
			#subprocess.call(launch_cmd, timeout = 60, shell=True)
			record_cmd = adb + 'shell screenrecord --time-limit 40 /sdcard/pageload.mp4'
			#subprocess.call(record_cmd, timeout = 60, shell=True)
			child_processes = []
			#out = open('my-process-out.txt', 'w')
			p1 = subprocess.Popen(launch_cmd, shell=True)
		        child_processes.append(p1)
			p2 = subprocess.call(record_cmd, shell=True)
			p1.wait()
			#for cp in child_processes:
			_page = site.split('//')[1].strip()
			_page = _page.split('/')[0].strip()
			_path = [video_output_base_dir, package_name, _page]
			video_output_dir = os.path.join('', *_path)
			if not os.path.exists(video_output_dir):
			    os.makedirs(video_output_dir)
			getVideo_cmd = "adb pull /sdcard/pageload.mp4 " + video_output_dir + "/" + _page + ".mp4" ;
			print('getVideo_cmd: ' + getVideo_cmd)
			subprocess.call(getVideo_cmd, shell=True)
			# load blank data for SpeedIndex purpose
			launch_blank_cmd = adb + 'shell am start -n ' + browser.strip() + ' ' + 'data:,'
			#time.sleep(5)
                        kill_app(package_name)
			subprocess.call(launch_blank_cmd, shell=True)
			time.sleep(7)
