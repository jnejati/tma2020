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
            #print(item)
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
    print(data,len(data))
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
        print(item)
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
    #util.tc()
    adb = Adb(devId)
    print('in crawl',apk)
    pkgId, apkName, browser, launAct,launMethod = apk
    datafolder = "data/%s/%s" %(pkgId,apkName)
    if os.path.exists(datafolder):
        subprocess.call(["rm","-r",datafolder])
    os.makedirs(datafolder)
    home_folder = os.path.expanduser("~")
    # fix the permission for this
    #adb.data_pull("/data/data/%s" %pkgId,"%s/%s" %(datafolder,pkgId))
    for url in websites:
        version = browser + '_run_' + str(run_no) + 'ON_A7'
        frag = '#'
        #if not url.endswith('/'):
        #frag  = '/' + frag
        _url = url + frag + version 
        print(_url)
        for i in range(4):
            adb.tap_ok()
        adb.launch_benchmark(pkgId,launAct,launMethod, _url, 200)
        #time.sleep(300)
        # chaange to previous directory
        util.kill_app(pkgId)
    adb.uninstall(pkgId)
    #time.sleep(4000)

def main(devId, api, apks):
    with open('../logs/apkslog.csv', 'w') as apks_log:
        for run_no in range(0,3):
            for apk in _apks:
                pkgId, apkName, browser = apk
                print('splash')
                """if browser.startswith('Fi') and run_no == 2:
                        continue
                if browser.startswith('Ch') and run_no == 2:
                        continue
                if browser.startswith('Ba') and run_no == 2:
                        continue
                if browser.startswith('Ks') and run_no == 2 :
                        continue
                if browser.startswith('Op') and run_no ==2:
                        continue
                if browser.startswith('Ya') and run_no ==2:
                        continue
                if browser.startswith('Tu') and run_no ==2:
                        continue"""
                splash = SplashBypass(pkgId, devId, apkName, api)
                launRes,launAct,bypaRes,launMethod = splash.main()
                print(launRes, bypaRes)
                print('visit testsuite')
                if bypaRes:
                    #if browser.startswith('#mx'):
                    websites = [item[0] for item in read_data("../config/testsuite.txt")]
                    #TEMP
                    print('browser:', browser)
                    if browser.startswith('xx') and run_no ==2:
                        _websites = websites[91:]
                    else:
                        _websites = websites
                    #TEMP
                    apkinfo = apk + [launAct,launMethod]
                    time.sleep(5)
                    crawl(apkinfo, _websites, run_no)
                    pkgId, apkName, browser = apk
                    print('visit testsuite')
                    apks_log.write(apkinfo[1] + '\n')
        #time.sleep(4000)


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
