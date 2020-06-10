#m!/usr/bin/python
import os,ast,time,shutil,subprocess
import lxml.etree as ET
from PIL import Image
try:
    from itertools import izip as zip
except ImportError: # will be 3.x series
    pass
# from itertools import izip
from difflib import SequenceMatcher


# from python files
from adb import Adb
from logger import logger

KEY_WORDS = ['guest login','next', 'allow','continue','ok','start','skip','accept','agree','no thanks',\
'launch','done','surf','yes','dismiss','set','bypass','browser','finish',
'later','try it','got it','understand','cancel','no','go','check']
BUTTON_TYPES = ['android.widget.Button','android.widget.TextView']

class SplashBypass():
    def __init__(self,pkgId,devId,apkName,SDKVersion):
        self.pkgId = pkgId
        self.devId = devId
        self.sdkVer = SDKVersion
        self.apkName = apkName
        # path to apk file
        self.apkPath = "../apks/" + self.pkgId + '/' + self.apkName
        # the page to demonstrate the rendering of random page succesfully.
        self.url = "http://pragsec-one.xyz/launch"
        self.adbCommander = Adb(self.devId)

    def configEnv(self):
        # capture homescreen and resolution [width,height] for device;
        device_ui = "tmp/device/%s" %self.devId
        cur_dir = "tmp/cur/%s" %self.devId
        if not os.path.exists(device_ui):
            os.makedirs(device_ui)
        if not os.path.exists(cur_dir):
            os.makedirs(cur_dir)
        dst = "%s/screen.png" %device_ui
        self.adbCommander.get_screenshot(dst)
        # define args for self.
        self.home_screen = dst
        self.resolution = self.displaySize(device_ui)

    def displaySize(self,device_ui):
        path = "%s/ui.xml" %device_ui
        self.adbCommander.get_layout(path)
        nodes = ET.parse(path).xpath("node")
        bound = nodes[0].get("bounds")
        # get resolution;
        tmp = ast.literal_eval(bound.replace("][","],["))
        width,height = int(tmp[1][0]),int(tmp[1][1])
        resolution = [width,height]
        return resolution

    def getActList(self):
        launActlist = None
        activity_list = {}
        with open("../config/pkg_activity.txt") as f:
            pkglist = f.readlines()
            for line in pkglist:
                line = line.strip('\n').split(' ')
                activity_list[line[0]] = line[1:]
        if len(activity_list[self.pkgId]) != 0:
            launActlist = activity_list[self.pkgId]
        return launActlist

    def install(self):
        code = self.adbCommander.install(self.pkgId,self.apkPath)
        if "INSTALL_FAILED_DEXOPT" in code:
            self.adbCommander.uninstall(self.pkgId)
            code = self.adbCommander.install(self.pkgId,self.apkPath)
        return code

    def launchBrowserIntent(self,activities):
        launAct = None
        res_launch = False
        launActlist = []
        try:
            basestring
        except NameError:
            basestring = str
        # relaunch case
        if isinstance(activities,basestring):
            launActlist.append(activities)
        else:
            launActlist = activities
        for act in launActlist:
            p1, out,err = self.adbCommander.launch_browser(self.pkgId,act,self.url)
            if (not "Error" in out) and (not "Error" in err):
                launAct = act
                res_launch = True
                break
        return res_launch,launAct

    def launchBrowserBroadcast(self, flag=True):
        p1, out,err = self.adbCommander.launch_broadcast(self.pkgId,self.url)
        # run for the first time
        if (not "Error" in out) and (not "Error" in err) and flag:
            res_b = True
            path = "tmp/cur/%s/ui.xml" %self.devId
            self.adbCommander.get_layout(path)
            tree = ET.parse(path)
            root = tree.getroot()
            if int(self.sdkVer) >= 21:
                title = root.xpath(".//*[contains(@text,'Open with') and \
                            @resource-id='android:id/title' and @class='android.widget.TextView']")
                if len(title) != 0:
                    if len(title[0].get('text')) == 9:
                        app_lists = root.xpath(".//*[@resource-id='android:id/text1' \
                                    and @class='android.widget.TextView']")
                        for app in app_lists:
                            sibling = app.getnext()
                            # Browser list has duplicate name "Browser"
                            if sibling is not None:
                                if sibling.get('text') != 'com.android.browser':
                                    app_button = app.get('bounds')
                                    button = ast.literal_eval(app_button.replace('][','],['))
                                    # tap
                                    self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2,\
                                                (int(button[1][1])+int(button[0][1]))/2)
                                    # always
                                    always = root.xpath(".//*[@resource-id='android:id/button_always' \
                                                and @class='android.widget.Button']")[0].get('bounds')
                                    button = ast.literal_eval(always.replace('][','],['))
                                    self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2,\
                                                (int(button[1][1])+int(button[0][1]))/2)
                            else:
                                if app.get('text') != "Browser" and "webview" not in app.get('text').lower():
                                    app_button = app.get('bounds')
                                    button = ast.literal_eval(app_button.replace('][','],['))
                                    # tap
                                    self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2,\
                                                (int(button[1][1])+int(button[0][1]))/2)
                                    # always
                                    always = root.xpath(".//*[@resource-id='android:id/button_always' \
                                                and @class='android.widget.Button']")[0].get('bounds')
                                    button = ast.literal_eval(always.replace('][','],['))
                                    self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2,\
                                                (int(button[1][1])+int(button[0][1]))/2)
                    # open with specific app;
                    else:
                        always = root.xpath(".//*[@resource-id='android:id/button_always' \
                                    and @class='android.widget.Button']")[0].get('bounds')
                        button = ast.literal_eval(always.replace('][','],['))
                        self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2,\
                                    (int(button[1][1])+int(button[0][1]))/2)
                # app not in the list
                else:
                    res_b = False
                    # using startN to launch app

            # 16,18
            else:
                title = root.xpath(".//*[@resource-id='android:id/alertTitle' and \
                         @class='android.widget.TextView' and @text='Complete action using']")
                if len(title) != 0:
                    app = root.xpath(".//*[@text !='Browser' and @text != 'Complete action using'\
                             and @class='android.widget.TextView']")[0]
                    app_button = app.get('bounds')
                    button = ast.literal_eval(app_button.replace('][','],['))
                    self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2, \
                                (int(button[1][1])+int(button[0][1]))/2)
                    # always
                    self.adbCommander.get_layout(path)
                    tree = ET.parse(path)
                    root = tree.getroot()
                    try:
                        always = root.xpath(".//*[@text='Always' and @class='android.widget.Button']")[0].get('bounds')
                        button = ast.literal_eval(always.replace('][','],['))
                        self.adbCommander.screen_tap((int(button[1][0])+int(button[0][0]))/2,\
                                    (int(button[1][1])+int(button[0][1]))/2)
                    except IndexError:
                        pass
                else:
                    res_b = False
                    # using startN to launch app
        else:
            res_b = False
        return res_b

    def saveState(self,flag):
        dirPath = "tmp/testapk/tmp/%s/%s/" %(self.devId,flag)
        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)
        imagePath = dirPath + "screen.png"
        OcrPath = dirPath + "output"
        xmlPath = dirPath + "ui.xml"
        self.adbCommander.get_screenshot(imagePath)
        ocrFile = self.getOcr(imagePath,OcrPath)
        ocr = self.readOcrText(ocrFile)
        self.adbCommander.get_layout(xmlPath)
        uiText = self.matchText(xmlPath)
        return ocr, uiText, imagePath, ocrFile, xmlPath

    def getOcr(self,imagePath,OcrPath):
        self.adbCommander.get_screenshot(imagePath)
        subprocess.call(['tesseract',imagePath,OcrPath],stdout = subprocess.PIPE)
        ocr_file = OcrPath+".txt"
        return ocr_file

    def readOcrText(self,ocrFile):
        ocr_file = open(ocrFile,'r')
        ocr = ocr_file.read().replace('\n',' ')
        return ocr

    def matchText(self,hierPath):
        try:
            xml_tree = ET.parse(hierPath)
            root = xml_tree.getroot()
            nodes = root.xpath("//node")
            uiText = ""
            for el in nodes:
                text = el.get('text')
                if text != "":
                    uiText = uiText +" "+ text
        except ET.XMLSyntaxError:
            uiText = ""
        except IOError:
            uiText = ""
        return uiText

    def comparison(self,imageA_path,imageB_path):
        i1 = Image.open(imageA_path)
        i2 = Image.open(imageB_path)
        assert i1.mode == i2.mode, "Different kinds of images."
        assert i1.size == i2.size, "Different sizes."

        pairs = zip(i1.getdata(), i2.getdata())
        if len(i1.getbands()) == 1:
                # for gray-scale images
            diff = 0
            ncomponents = 0
            for p1,p2 in pairs:
                if abs(p1-p2) != 0:
                    diff += 1
            ncomponents = i1.size[0] * i1.size[1]
        else:
            # for other image types
            diff = 0
            ncomponents = 0
            for p1,p2 in pairs:
                for c1,c2 in zip(p1,p2):
                    if abs(c1-c2) != 0:
                        diff += 1
            ncomponents = i1.size[0] * i1.size[1] * 3
        percentage = float(diff * 100) / float(ncomponents)
        return percentage

    def moveFile(self,imagePath,ocrFile,xmlPath,flag):
        logger.info("Moving splash state files: dev: {0}\nbrowser: {1}"\
                .format(self.devId, self.apkName))
        destPath = "tmp/testapk/result/%s/" %self.pkgId
        if not os.path.isdir(destPath):
            os.makedirs(destPath)
        shutil.move(imagePath,destPath+self.apkName+"-"+flag+".png")
        shutil.move(ocrFile,destPath+self.apkName+"-"+flag+".txt")
        shutil.move(xmlPath,destPath+self.apkName+"-"+flag+".xml")
        return None

    def CheckBox(self,hierPath):
        xml_tree = ET.parse(hierPath)
        root = xml_tree.getroot()
        pattern = ".//*[@class='%s' and @checkable='true']" %"android.widget.CheckBox"
        match = root.xpath(pattern)
        if len(match) != 0:
            clickElements = self.getButtonLoc(match)
            for i in clickElements:
                loc_x = i[0]
                loc_y = i[1]
                self.adbCommander.screen_tap(loc_x,loc_y)
        return None

    def getButtonLoc(self,matchElement):
        clickElements = []
        for el in matchElement:
            bounds = el.get("bounds")
            index = bounds.find("][")
            bounds = bounds[:index+1]+","+bounds[index+1:]
            bounds = bounds.replace("[","").replace("]","").split(",")
            loc_x = int((int(bounds[0])+int(bounds[2]))/2)
            loc_y = int((int(bounds[1])+int(bounds[3]))/2)
            clickElements.append([loc_x,loc_y])
        return clickElements

    def matchText(self,hierPath):
        try:
            xml_tree = ET.parse(hierPath)
            root = xml_tree.getroot()
            nodes = root.xpath("//node")
            uiText = ""
            for el in nodes:
                text = el.get('text')
                if text != "":
                    uiText = uiText +" "+ text
        except ET.XMLSyntaxError:
            uiText = ""
        except IOError:
            uiText = ""
        return uiText

    def matchClickButton(self,hierPath,word):
        xml_tree = ET.parse(hierPath)
        root = xml_tree.getroot()
        # and @clickable='true'
        pattern_tp1 = ".//*[@class='%s' and contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % (BUTTON_TYPES[0],word)
        pattern_tp2 = ".//*[@class='%s' and contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % (BUTTON_TYPES[1],word)
        logger.info("matchClickButton: dev: {0}\nbrowser: {1}\npattern: {2}"\
                .format(self.devId, self.apkName,pattern_tp1))
        logger.info("matchClickButton: dev: {0}\nbrowser: {1}\npattern: {2}"\
                .format(self.devId, self.apkName,pattern_tp2))
        match = root.xpath(pattern_tp1) + root.xpath(pattern_tp2)
        logger.info("matchClickButton: dev: {0}\nbrowser: {1}\nmatch: {2}"\
                .format(self.devId, self.apkName,str(match)))
        result = []
        if len(match) != 0:
            for element in match:
                if len(element.get("text").split(" ")) > 5:
                    print("Removing matched button for: " + element.get('text'))
                    match.remove(element)
        if len(match) != 0:
            print(match[0].get('text'))
            prob = SequenceMatcher(None,match[0].get('text').lower(),word).ratio()
            print(prob)
            if prob > 0.4:
                result.append(match[0])
                logger.info("matchClickButton: dev: {0}\nbrowser: {1}\nword: {2}"\
                            .format(self.devId, self.apkName, match[0].get('text').lower()))
                logger.info("matchClickButton: dev: {0}\nbrowser: {1}\nprabaility: {2}"\
                            .format(self.devId, self.apkName, str(prob)))
            else:
                prob = 0
            # multiple matches
            if len(match) > 1:
                for item in match:
                    sim = SequenceMatcher(None,item.get('text').lower(),word).ratio()
                    logger.info("matchClickButton: dev: {0}\nbrowser: {1}\nword: {2}"\
                            .format(self.devId, self.apkName, item.get('text').lower()))
                    logger.info("matchClickButton: dev: {0}\nbrowser: {1}\nprabaility: {2}"\
                                .format(self.devId, self.apkName, str(sim)))
                    if sim > prob and sim > 0.4:
                        prob = sim
                        if len(result) == 0:
                            result.append(item)
                        else:
                            result[0] = item
            if len(result) != 0:
                logger.info("matchClickButton: dev: {0}\nbrowser: {1}\n\nword: {2}\nprabaility: {3}"\
                        .format(self.devId, self.apkName, result[0].get('text'),str(prob)))
        return result

    def pageCheck(self,launAct,last_png,method):
        time.sleep(2)
        flag = "2"
        bypaRes = False
        bypaStat = ""
        last_page = "tmp/testapk/tmp/%s/" %self.devId
        if not os.path.isdir(last_page):
            os.makedirs(last_page)
        last_page = last_page+"last.png"
        shutil.copy2(last_png,last_page)
        ocr,uiText,imagePath,ocrFile,xmlPath = self.saveState(flag)
        if "hello" in ocr and "world" in ocr:
            bypaRes = True
            return bypaRes,bypaStat
        diff = self.comparison(self.home_screen,imagePath)
        if diff < 10:
            self.relaunch(launAct,method)
            bypaStat = "No&Continue"
            return bypaRes,bypaStat
        # print("with Home: " +str(diff))
        diff = self.comparison(last_page,imagePath)
        if diff < 3:
            bypaStat = "No&Next"
        else:
            bypaStat = "No&Continue"
        # print("With last: "+str(diff))
        return bypaRes,bypaStat

    def relaunch(self,launAct,method):
        if method == "IntentN":
            self.launchBrowserIntent(launAct)
        else:
            self.launchBrowserBroadcast()

    def splash_bypass(self,launAct,method):
        flag = "2"
        ocr,uiText,imagePath,ocrFile,xmlPath = self.saveState(flag)
        if "hello" in ocr and "world" in ocr:
            bypaRes = True
            self.moveFile(imagePath,ocrFile,xmlPath,"2")
            return bypaRes
        else:
            # device with uiautomator, bypass splash
            bypaRes = self.bypass(launAct,imagePath,xmlPath,method)
            self.moveFile(imagePath,ocrFile,xmlPath,"2")
        return bypaRes

    def bypass(self,launAct,last_png,xmlPath,method):
        bypaRes = False
        flag = "2"
        j = 1
        button_time = 0
        FromButton = False
        while j<7:
            logger.info("Splash bybassing: dev: {0}\nbrowser: {1}\nround: {2}"\
                    .format(self.devId, self.apkName,str(j)))
            if FromButton:
                button_time += 1
            else:
                FromButton = False
            # check checkable box;
            try:
                self.CheckBox(xmlPath)
            except ET.XMLSyntaxError:
                pass
            # method 1: find button;
            logger.info("Splash bybassing: identifying matched buttons: dev: {0}\nbrowser: {1}"\
                .format(self.devId, self.apkName))
            uiText = self.matchText(xmlPath)
            for word in KEY_WORDS:
                print(word)
                if word in uiText.lower():
                    print(word)
                    print(uiText.lower())
                    # only the most match element is selected, matchElement is 1;
                    matchElement = self.matchClickButton(xmlPath,word)
                    logger.info("Matching buttons: dev: {0}\nbrowser: {1}\nword: {2}"\
                            .format(self.devId, self.apkName, word))
                    if len(matchElement) != 0:
                        clickElements = self.getButtonLoc(matchElement)
                        loc = clickElements[0]
                        self.adbCommander.screen_tap(loc[0],loc[1])
                        logger.info("Tapping on screen: dev: {0}\nbrowser: {1}\nposition: {2}"\
                                .format(self.devId, self.apkName, str(str(loc[0]))+","+str(loc[1])))
                        break
                    else:
                        continue
            bypaRes,bypaStat = self.pageCheck(launAct,last_png,method)
            if bypaRes:
                break
            elif button_time < 7 and "Continue" in bypaStat:
                j += 1
                continue
            # method 2: swipe instead;
            logger.info("Swiping screen: dev: {0}\nbrowser: {1}"\
                .format(self.devId, self.apkName))
            end_x = str(50)
            start_x = str(self.resolution[0]-50)
            y = str(self.resolution[1]/2)
            self.adbCommander.screen_swipe(7,start_x,y,end_x,y)
            bypaRes,bypaStat = self.pageCheck(launAct,last_png,method)
            if bypaRes:
                break
            elif "Continue" in bypaStat:
                j += 1
                continue

            # method 3: consider the ad;
            logger.info("Bypassing ad: dev: {0}\nbrowser: {1}"\
                    .format(self.devId, self.apkName))
            self.adbCommander.key_event(4)
            self.relaunch(launAct,method)
            time.sleep(2)
            bypaRes,bypaStat = self.pageCheck(launAct,last_png,method)
            if bypaRes:
                break
            elif "Continue" in bypaStat:
                j += 1
                continue

            # another launch without back
            self.relaunch(launAct,method)
            time.sleep(2)
            bypaRes,bypaStat = self.pageCheck(launAct,last_png,method)
            if bypaRes:
                break
            else:
                j += 1
                continue
            # no words found, click right most button;
            #dprint("bypass","find rightmost button")
            #loc = rightButton(xmlPath)
            #if len(loc) != 0:
            #    screenTap(deviceId,loc[0],loc[1])
            #    dprint("screenTap","tap on "+str(loc[0])+","+str(loc[1]))
            #j = j + 1
        if "No" in bypaStat:
            bypaRes = False
        return bypaRes

    def splashDetect(self):
        launRes = None
        launAct = None
        bypaRes = False
        launMethod = "IntentN"
        metlist = [launMethod]
        self.adbCommander.reset_browser_data(self.pkgId)
        code = self.install()

        if "Failure" in code:
            failCode = code.split(" ")[1]
            logger.error("Installation Failure: dev: {0}\nbrowser: {1}\ncode: {2}"\
                .format(self.devId, self.apkName,failCode))
        else:
            activities = self.getActList()
            if activities == None:
                logger.error("Unable to find launchabl activity: dev: {0}\nbrowser: {1}"\
                .format(self.devId, self.apkName))
                return launRes,launAct,bypaRes,launMethod
            launRes,launAct = self.launchBrowserIntent(activities)
            if not launRes:
                launRes = self.launchBrowserBroadcast()
                launMethod = "Broadcast"
                metlist = [launMethod]
            else:
                metlist.append("Broadcast")
            for method in metlist:
                self.relaunch(activities,method)
                flag = "1"
                time.sleep(15)
                ocr,uiText,imagePath,ocrFile,xmlPath = self.saveState(flag)
                diff = self.comparison(self.home_screen,imagePath)
                if diff < 10:
                    launRes = "Not launched(No app window)"
                    self.adbCommander.uninstall(self.pkgId)
                    launMethod = method
                    return launRes,launAct,bypaRes,launMethod
                elif "hello" in ocr and "world" in ocr:
                    launRes = "No splash"
                    self.moveFile(imagePath,ocrFile,xmlPath,flag)
                    launMethod = method
                    bypaRes = True
                    break
                else:
                    if "crashed" in ocr or "stopped" in ocr:
                        launRes = "App with splash(crash message)"
                    else:
                        launRes = "App with splash"
                    # if launAct is not None(-n), else(-p)
                    bypaRes = self.splash_bypass(launAct,method)
                    if bypaRes:
                        launMethod = method
                        self.moveFile(imagePath,ocrFile,xmlPath,"1")
                        break
                    else:
                        launMethod = method
                        self.moveFile(imagePath,ocrFile,xmlPath,"1")
        return launRes,launAct,bypaRes,launMethod

    def main(self):
        # config
        self.configEnv()
        print(self.home_screen)
        print(self.resolution)
        # splash bypassing
        launRes,launAct,bypaRes,launMethod = self.splashDetect()
        return launRes,launAct,bypaRes,launMethod

if __name__ == "__main__":
    # pkgId,devId,apkName,SDKVersion
    splash = SplashBypass("com.android.chrome","84B5T15B04001727","com.android.chrome_68.0.3440.91-344009152.apk","25")
    # splash = SplashBypass("org.mozilla.firefox","04ce922400745111","org.mozilla.firefox_61.0-2015565729-23.apk","23")
    splash.main()
