#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from config import CrawlerConfig
import os
import sys
import subprocess
import time
from logger import logger

#TODO:Add -s option in all APIs to enable talking ot a particular device
#

class Adb():
    def __init__(self, devId="dummy"):
        self.get_devices()
        self.devId = devId
        self.mkdir()
        # pass

    @staticmethod
    def get_devices():
        data = subprocess.check_output("adb devices -l", shell=True)
        data = data.split(b'\n')
        # data = (proc.stdout.read()).split("\n")
        data = data[1:]# remove header line ,device start from 1
        data = [x for x in data if x] # remove empty strings
        # print('data: ', data)
        devices = []
        for line in data:
            # print('line: ', line)
            dev = (line.split(b" ")[0]).strip().decode('utf-8')
            devices.append(dev)
        # print('devices: ',devices)
        return devices

    def get_prop(self,attr):
        proc = subprocess.Popen(["adb","-s",self.devId,"shell","getprop"],  stdout=subprocess.PIPE)
        if attr != False:
            for line in proc.stdout:
                line = line.strip()
                if attr in line:
                    line = line.split(" ")[1].replace("[","").replace("]","")
                    return line
            return None
        else:
            return p.communicate()[0].decode('utf-8')

    def set_proxy(self,proxy):
        subprocess.call(['adb','-s',self.devId, 'shell',\
                'settings','put', 'global', 'http_proxy', proxy])

    def del_proxy(self):
        subprocess.call(['adb','-s',self.devId, 'shell',\
                'settings','delete', 'global', 'http_proxy'])
        subprocess.call(['adb','-s',self.devId, 'shell',\
                'settings','delete', 'global', 'global_http_proxy_host'])
        subprocess.call(['adb','-s',self.devId, 'shell',\
                'settings','delete', 'global', 'global_http_proxy_port'])

    def reset_home_screen(self):
        self.reboot()
        time.sleep(40)
        # unlock screen with passcode
        if self.devId == "84B5T15B04001727":
            self.screen_tap(1100,1400)
            # unlock with passcode
            self.screen_swipe(1,930,880,930,380)
            self.text_key_event("1234", "KEYCODE_ENTER")
        else:
            # unlock screen
            self.key_event("KEYCODE_MENU")
        self.key_event("KEYCODE_HOME")

    def reset(self):
        self.del_proxy()
        self.reset_home_screen()

    def start_server(self):
        subprocess.Popen(['adb','start-server'])

    def kill_emulator(self):
        subprocess.Popen(['adb', 'emu', 'kill'])

    #launches emulated device
    def start_device(self, name='Pixel_XL_API_27'):
        # emulator is put into environment variables;
        # Path: '~/Android/Sdk/tools/emulator'
        subprocess.Popen(['emulator','-netdelay','none',\
            '-netspeed','full','-avd',name])

    def factory_reset(self):
        #TODO: does not work
        subprocess.call(['adb','-s',self.devId,'shell',\
            'am', 'broadcast', '-a', 'android.intent.action.MASTER_CLEAR'])

    def chroot(self):
        subprocess.call(['adb','-s',self.devId,'root'])
        subprocess.call(['adb','-s',self.devId,'remount'])

    def install(self,pkgId,apkPath):
        try:
            p = subprocess.Popen(['adb','-s',self.devId,'install',apkPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = p.communicate()
            print('out, error', out, err)
            out = out.decode('utf-8')
            err = err.decode('utf-8')
            print('new_out, new_error', out, err)
        except subprocess.CalledProcessError:
            pass
        if out != "":
            out = out.splitlines()[-1:][0]
        code = out + err
        logger.info("installing browser: device : {0}, app:{1}, apk:{2}, status:{3}".\
                    format(self.devId, pkgId, apkPath, code))
        # print('code: ', code)
        # print('code-utf-8: ' , code.decode('utf-8'))
        return code

    def uninstall(self,pkgId):
        subprocess.call(['adb','-s',self.devId,"uninstall",pkgId])

    def stop_app(self,pkgId):
        logger.debug("stopping app: device-{0}, app-{1}".format(self.devId, pkgId))
        # _cmd = """adb -s %s shell "su -c 'am force-stop %s'" """ % (self.devId,pkgId)
	# subprocess.call(_cmd, shell=True)
        subprocess.call(['adb','-s',self.devId ,'shell', 'am','force-stop', pkgId])

    def launch_browser_orig(self,pkgId,launActivity,url='about:blank'):
        logger.debug("launch_browser_intent: device : {0}, app:{1}, activity:{2}, url:{3}".\
                    format(self.devId,pkgId,launActivity,url))
        runComponent = pkgId+"/"+launActivity
        print('runComponent: ', runComponent)
        proc = subprocess.Popen(['adb','-s',self.devId,'shell', 'am','start',\
                 '-n', runComponent,'-a','android.intent.action.VIEW','-d',url],\
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return out,err

    def launch_broadcast_orig(self,pkgId,url='about:blank'):
        logger.debug("launch_browser_broadcast: device : {0}, app:{1}, url:{2}".\
                    format(self.devId,pkgId,url))
        proc = subprocess.Popen(['adb','-s',self.devId,'shell', 'am','start',\
                '-a','android.intent.action.VIEW','-d',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = proc.communicate()
        return out,err

    def launch_browser(self,pkgId,launActivity,url='about:blank'):

        logger.debug("launch_browser_intent: device : {0}, app:{1}, activity:{2}, url:{3}".\
                    format(self.devId,pkgId,launActivity,url))
        runComponent = pkgId+"/"+launActivity
        proc = subprocess.Popen(['adb','-s',self.devId,'shell', 'am','start',\
                 '-n', runComponent,'-a','android.intent.action.VIEW','-d',url],\
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc, out.decode('utf-8'),err.decode('utf-8')

    def launch_broadcast(self,pkgId,url='about:blank'):
        logger.debug("launch_browser_broadcast: device : {0}, app:{1}, url:{2}".\
                    format(self.devId,pkgId,url))
        proc = subprocess.Popen(['adb','-s',self.devId,'shell', 'am','start',\
                '-a','android.intent.action.VIEW','-d',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = proc.communicate()
        return proc, out.decode('utf-8'),err.decode('utf-8')

    def launch_url(self,pkgId,launAct,launMethod,url='about:blank'):
        if launMethod == "IntentN":
            p1, s1, s2 = self.launch_browser(pkgId,launAct,url)
        else:
            p1, s1, s2 = self.launch_broadcast(pkgId,url)
    
    def launch_benchmark(self,pkgId,launAct,launMethod, url, wait_time):
        if launMethod == "IntentN":
            p1, s1, s2 = self.launch_browser(pkgId,launAct,url)
        else:
            p1, s1, s2 = self.launch_broadcast(pkgId,url)
        cmd = 'sleep ' + str(wait_time)
        p2 = subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
        p1.wait()

    def launch_url_video(self,pkgId,launAct,launMethod,_apk,run_no, is_archive=False, url='about:blank'):
        adb_cmd ='/usr/bin/adb -s ' + self.devId + ' '
        video_output_base_dir = '/home/jnejati/videos'
        record_cmd = adb_cmd + 'shell screenrecord --time-limit 40 /sdcard/pageload.mp4'
	    #child_processes = []
        if launMethod == "IntentN":
            p1, s1, s2 = self.launch_browser(pkgId,launAct,url)
        else:
            p1, s1, s2 = self.launch_broadcast(pkgId,url)
        #child_processes.append(p1)
        p2 = subprocess.call(record_cmd, shell=True)
        #p1.wait(timeout = 10)
        p1.wait()
        #http://web.archive.org/web/20190320212851/https://www.xing.com/
        url = url.split('//#')[0]
        print('url: ', url)
        if is_archive:
            url = url.split('//#')[0]
            _page = url.split('//')[2].strip()
        else:
            url = url.split('/#')[0]
            _page = url.split('//')[1].strip()
        print('page: ', _page)
        _path = [video_output_base_dir, pkgId,_apk,_page,run_no]
        print('path: ', _path)
        video_output_dir = os.path.join('', *_path)
        if not os.path.exists(video_output_dir):
            os.makedirs(video_output_dir)
        getVideo_cmd = adb_cmd + " pull /sdcard/pageload.mp4 " + video_output_dir + "/" + _page + ".mp4" ;
        logger.debug("getVideo_cmd: {0}".format(getVideo_cmd))
        #subprocess.call(getVideo_cmd, timeout = 60, shell=True)
        subprocess.call(getVideo_cmd, shell=True)
        # load blank data for SpeedIndex purpose
        #runComponent = pkgId+"/"+launAct
        if launMethod == "IntentN":
            runComponent = pkgId+"/"+launAct
            launch_blank_cmd = adb_cmd +  ' shell am start -n ' \
                 + runComponent + ' -a android.intent.action.VIEW -d data:,'
        else:
            launch_blank_cmd = adb_cmd + ' shell am start' \
                 + ' -a android.intent.action.VIEW -d data:,'
	    subprocess.call(launch_blank_cmd, shell=True)
	    time.sleep(5)
	
    def get_dump(self, local_screenshot, local_layout, \
                target_screenshot='/sdcard/tmp/destination.png', target_layout='/sdcard/tmp/ui.xml'):
        self.get_screenshot(local_screenshot, cdc)
        self.get_layout(local_layout,target_layout)

    def get_screenshot(self, local, target='/sdcard/tmp/destination.png',jpeg=True):
        # _cmd = """adb -s %s shell "su -c 'screencap -p %s '" """ % (self.devId, target)
        # subprocess.call(_cmd, shell=True)
        subprocess.call(['adb', '-s', self.devId , 'shell', 'screencap', '-p', target])
        subprocess.call(['adb', '-s', self.devId,'pull',target,local])
        # if jpeg:
        #     src = local+target.split('/')[-1]
        #     logger.debug("converting to JPG: {0}".format(src))
        #     subprocess.call(['mogrify','-format', 'jpg', src])
        #     subprocess.call(['rm','-f',src])

    def get_layout(self, local, target='/sdcard/tmp/ui.xml'):
        #_cmd = """adb -s %s shell "su -c 'uiautomator dump %s '" """ % (self.devId, target)
        #subprocess.call(_cmd, shell=True)
        subprocess.call(["adb","-s",self.devId,"shell","uiautomator","dump",target])
        subprocess.call(["adb","-s",self.devId,"pull",target,local])

    def screen_tap(self,loc_x,loc_y):
        subprocess.call(["adb","-s",self.devId,"shell","input","tap",str(loc_x),str(loc_y)])

    def screen_swipe(self,ts,start_x,start_y,end_x,end_y):
        for i in range(ts):
            subprocess.call(["adb","-s",self.devId,"shell","input","swipe", str(start_x), str(start_y), str(end_x), str(end_y)])
            time.sleep(1)

    def key_event(self,code):
        subprocess.call(['adb','-s',self.devId,'shell','input','keyevent',str(code)])

    def text_event(self, text):
        subprocess.call(['adb','-s',self.devId,'shell','input','text', text])

    def text_key_event(self, text, code):
        self.text_event(text)
        self.key_event(code)
        # subprocess.call(['adb','-s',self.devId,'shell','input','text', text,\
        #             '&&','adb','-s',self.devId,'shell','input','keyevent',str(code)])

    def clear_previous_captures(self):
        # _cmd = """adb -s %s shell "su -c 'rm -f /sdcard/tmp/*'" """ % (self.devId)
        # print(_cmd)
        # subproess.call(_cmd, shell=True)
	subprocess.call(['adb','-s', self.devId, 'shell', 'rm', '-f','/sdcard/tmp/*'])

    def reset_browser_data(self,pkgId):
        datapath = '/data/data/' + pkgId +"/*"
        logger.debug("app: {0}, resetting datapath: {1}".format(pkgId, datapath))
        # _cmd = """adb -s %s shell "su -c 'rm -rf %s '" """ % (self.devId, datapath)
        # subprocess.call(_cmd, shell=True)
        subprocess.call(['adb','-s', self.devId, 'shell', 'rm', '-rf',datapath])

    def clear_cookies(self,pkgId):
        datapath1=''
        datapath2=''
        srcpath = "/data/data/" + pkgId
        if pkgId == 'com.android.chrome':
            datapath1 = srcpath + '/*cache'
            datapath2 = srcpath + '/app*'
            # $data_ac_dir = /app_chrome
            # "$data_ac_dir/History* $data_ac_dir/Web\ Data* $data_ac_dir/Cookies* \
            # $data_ac_dir/Visited\ Links $data_ac_dir/Favicons* $data_ac_dir/Top\ Sites* \
            # $data_ac_dir/Login\ Data* $data_dir/app_tabs/0/* $data_dir/app_chrome/Local\ State;"

        elif pkgId == 'org.mozilla.firefox':
            datapath1 = srcpath + '/cache/*.default'
            datapath2 = srcpath + '/files/mozilla/*.default/'
            files = subprocess.check_output(["adb","-s",self.devId,"shell","ls","%s" %datapath2]).splitlines()
            for item in files:
                if "cert" in item:
                    files.remove(item)
            datapath2 = " ".join([datapath2+item for item in files])

        logger.debug("app: {0}, cleaning datapaths: {1}, {2}".format(pkgId, datapath1, datapath2))
        # _cmd = """adb -s %s shell "su -c 'rm -rf %s %s '" """ % (self.devId, datapath1, datapath2)
        # subprocess.call(_cmd, shell=True)
        subprocess.call(['adb','-s',self.devId ,'shell', 'rm', '-rf',\
                  datapath1, datapath2])

    def close_previous_tabs(self,pkgId):
        datapath = ''
        srcpath = "/data/data/" + pkgId
        if pkgId == 'com.android.chrome':
            datapath = srcpath + '/app_tabs/'
        elif pkgId == 'org.mozilla.firefox':
            datapath = srcpath + '/cache/*.default'
        # _cmd = """adb -s %s shell "su -c 'rm -rf %s '" """ % (self.devId, datapath)
        # subprocess.call(_cmd, shell=True)
        subprocess.call(['adb','-s',self.devId,'shell', 'rm',\
             '-rf', datapath])

    def fetch_data(self,pkgId,datafolder):
        logger.debug("fetching browsing data: app: {0}, device: {1}".format(pkgId,self.devId))
        files = subprocess.check_output(["adb","-s",self.devId,"shell","ls","/data/data/%s" %pkgId]).splitlines()[:-1]
        if pkgId == "org.mozilla.firefox":
            for item in ["lib","fonts"]:
                files.remove(item)
        elif pkgId == "com.android.chrome":
            for item in ["lib"]:
                files.remove(item)
        for item in files:
            subprocess.call(["adb","-s",self.devId,"pull","/data/data/%s/%s" %(pkgId,item), "%s/%s" %(datafolder,pkgId)])

    def data_pull(self, devPath, localPath):
        print('Inside data_pull...')
        subprocess.call(['adb', '-s',self.devId,'pull', devPath, localPath])

    def data_push(self, localPath, devPath):
        print('in data_push')
        subprocess.call(["adb","-s",self.devId,"push",localPath,devPath])

    def data_clear(self,pkgId):
        print('in data_clear')
        print('cmd = ', "adb -s ",self.devId, "shell", "pm", "clear" ,pkgId)
        subprocess.call(["adb","-s",self.devId,"shell", "pm","clear",pkgId])

    def restore_data(self,pkgId,datafolder):
        logger.debug("restoring browsing data: app: {0}, device: {1}".format(pkgId,self.devId))
        subprocess.call(["adb","-s",self.devId,"push", "%s/%s" %(datafolder,pkgId),"/sdcard/"])

        # _cmd = """adb -s %s shell "su -c 'mv /sdcard/%s /data/data/'" """ % (self.devId, pkgId)
        # subprocess.call(_cmd, shell=True)
        subprocess.call(["adb","-s",self.devId,"shell","mv","/sdcard/%s"%pkgId,"/data/data/"])

    def mkdir(self, name='/sdcard/tmp'):
        # _cmd = """adb -s %s shell "su -c 'mmkdir %s '" """ % (self.devId, name)
        # subprocess.call(_cmd, shell=True)
        subprocess.call(['adb', '-s',self.devId,'shell', 'mkdir', name])

    def reboot(self):
        subprocess.call(['adb', '-s', self.devId,'reboot'])
        #poweroff - adb -s emulator-5554 shell reboot -p

    def tap_ok(self):
        subprocess.call(['adb', 'shell', 'input', 'keyevent', '66'])

if __name__=="__main__":
    print ("testing adb class")
    adb = Adb()
    adb.chroot(False)
