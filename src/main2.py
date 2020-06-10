#!/usr/bin/python
from adb import Adb
import time,os,subprocess
import collections
from splash import SplashBypass
import multiprocessing
import iptables
import util

def read_data(fname, sep="\t", start=1):
    data = []
    with open(fname) as f:
        for item in f.readlines()[start:]:
            if item.startswith('#'):
                continue
            item = item.strip().split(sep)
            # print(item)
            data.append(item)
    return data

def find_mapping_year(minSdk, year, year_api_code, maxYear):
    if year in year_api_code:
        # print('year, minSdk: ',minSdk, year, int(year_api_code[year][0]) )
        if int(minSdk) <= int(year_api_code[year][0]):
            # print('inside...')
            return year_api_code[year][0]
        else:
            _year = int(year) + 1
            while _year <= maxYear:
                if int(minSdk) <= int(year_api_code[str(_year)][0]):
                    # print(year, year_api_code[year], year_api_code[str(_year)][0])
                    return year_api_code[str(_year)][0]
                _year+=1
            return None


def apk_device_map(conn_devs={},apkfile="../config/apk_sample_test.csv"):
    year_api_code = dict()
    data = read_data("../config/apk_Androidsys_code0.txt", sep=",")
    prev = ""
    for item in data:
        year, version, api, code = item
        if year == '':
            year = prev
            year_api_code[year].append(api)
        else:
            prev = year
            year_api_code.update({year:[api]})
    apks = collections.defaultdict(list)
    #print(year_api_code)
    
    # map apk to dev's sdk
    available_apis = [ int(x) for x in list(conn_devs.keys())]
    data = read_data(apkfile, sep=",")
    # print(len(data))
    for apk in data:
        try:
            pkgId, apkName, browser, minSdk, tarSdk, maxSdk, year = apk
        except ValueError as e:
            print('error', e, apk)
            exit()
        if tarSdk == '' or minSdk == '':
            continue
        # pkgId, devId, apkName, AndroidSysVer
        try:
            apis = year_api_code[year]
        except KeyError:
            apis = []
        max_year = int(max(year_api_code.keys()))
        # check if the sdk is bigger than minSdk version
        _api = find_mapping_year(minSdk, year, year_api_code, max_year)
        if _api is None:
            # print('None...')
            continue
        apks[_api].append([pkgId,apkName,browser])
    return apks

def get_devices():
    # device api
    devs = {}
    data = read_data("../config/device_info.txt")
    for item in data:
        api, dev = item
        devs.update({api:dev})

    conn_devs = Adb.get_devices()
    # print('conn_dev:', conn_devs)
    # print('devs: ', devs)
    _devs = dict()
    for dev, api in devs.items():
        # print(dev, api)
        if dev in conn_devs:
            _devs.update({api:dev})
    return _devs

def crawl(apk,websites,run_no):
    adb = Adb(devId)
    print('in crawl',apk)
    pkgId, apkName, browser, launAct,launMethod = apk
    datafolder = "data/%s/%s" %(pkgId,apkName)
    if os.path.exists(datafolder):
        subprocess.call(["rm","-r",datafolder])
    os.makedirs(datafolder)
    home_folder = os.path.expanduser("~")
    # fix the permission for this
    adb.data_pull("/data/data/%s" %pkgId,"%s/%s" %(datafolder,pkgId))
    for url in websites:
        for _run in range(run_no):
            version = browser + '_run_' + str(_run)
            frag = '#'
            if not url.endswith('/'):
                frag  = '/' + frag
            _url = url + frag + version
            print(_url)
            for i in range(4):
                adb.tap_ok()
            adb.launch_url_video(pkgId,launAct,launMethod,apkName,str(_run),_url)
            time.sleep(5)
            #adb.data_clear(pkgId)
            adb.data_push("%s/%s" %(datafolder,pkgId),"/data/data/")
            os.chdir(home_folder+"/bperf/src/%s/%s" %(datafolder,pkgId))
            # change su -c the last part
            ###########what is this supposed to do "su -c 'mv /sdcard/%s /data/data/'"
            _cmd = """find "." -type d -empty | sed 's/\.\///g'|xargs -I {} adb -s %s shell "su -c 'mkdir -p /data/data/%s/{}'" """ %(devId, pkgId)
            #subprocess.call("find . -type d -empty | sed 's/\ /\\\ /g' | sed 's/\./\/data\/data\/%s/' | awk '{system(\"adb -s %s shell mkdir -p \"$0)}'" %(pkgId,devId),shell=True)
            #print('mkdir cmd --->', _cmd)
            subprocess.call(_cmd, shell=True)
            # chaange to previous directory
            os.chdir(home_folder+"/bperf/src")
            #adb.close_previous_tabs(pkgId)
            #adb.clear_cookies(pkgId)
            util.kill_app(pkgId)
    adb.uninstall(pkgId)
    #time.sleep(4000)

def main(devId, api, apks):
    fw = iptables.Fw()
    with open('../logs/apkslog.csv', 'w') as apks_log:
        for apk in _apks:
            pkgId, apkName, browser = apk
            print('splash')
            splash = SplashBypass(pkgId, devId, apkName, api)
            launRes,launAct,bypaRes,launMethod = splash.main()
            print(launRes, bypaRes)
            print('visit testsuite')
            if bypaRes:
                #if browser.startswith('#mx'):
                websites = [item[0] for item in read_data("../config/testsuite.txt")]
                apkinfo = apk + [launAct,launMethod]
                fw.flush()
                fw.bypass()
                time.sleep(45)
                fw.flush()
                fw.redirect()
                time.sleep(5)
                crawl(apkinfo, websites, 5)
                pkgId, apkName, browser = apk
                print('splash')
                splash = SplashBypass(pkgId, devId, apkName, api)
                launRes,launAct,bypaRes,launMethod = splash.main()
                print(launRes, bypaRes)
                print('visit testsuite')
                apks_log.write(apkinfo[1] + '\n')
            time.sleep(4000)

if __name__ == "__main__":
    # get connected devices
    conn_devs = get_devices()
    print('conn_devs: ', conn_devs)

    # read apks for each device
    # trigger splash bypass, and then visit each websites
    instance = 0
    proc_list = []
    pid_l = []
    apks = apk_device_map(conn_devs)
    print('apks', apks)
    for api, _apks in apks.items():
        if api not in conn_devs:
            continue
        devId = conn_devs[api]
        p = multiprocessing.Process(name=str(api)+"_process", target=main, args=(devId,api,apks,))
        proc_list.append(p)
        pid_l.append(p.name)
        p.start()
