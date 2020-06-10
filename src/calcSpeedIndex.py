#!/usr/bin/env python
import os
import subprocess

videos = '/home/jnejati/videos/'
output_folder = '/home/jnejati/results/speedIndex/Marshmallow/all_pages.csv'
speedIndexDict = dict()

with open(output_folder, 'w') as out_f:
    out_f.write('browser,site,speedIndex\n')
    for path, subdirs, files in os.walk(videos):
        for name in files:
            siteName = path.split('/')[-1]
            packageName = path.split('/')[-2]
            videoFile = os.path.join(path, name)
            site = siteName.rstrip()
            #TODO package name should reflect version
            speedIndexDict[packageName] = dict()
            visualmetricsObject = subprocess.Popen(['python', '/home/jnejati/bperf/src/visualmetrics.py', '--video', videoFile, '--full', '--force'],\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = visualmetricsObject.communicate()
            metricsInfo = stdout
            metricsParsed = metricsInfo.split("Speed Index: ")
            print(metricsInfo)
            try:
                speedParse = metricsParsed[1]
            except:
                continue
            SpeedIndex = speedParse.split("\n")[0]
            speedIndexDict[packageName][siteName] = SpeedIndex
            print(siteName, packageName, SpeedIndex)
            out_f.write(packageName + ',' + siteName + ',' + SpeedIndex + '\n')
