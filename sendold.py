#! /usr/bin/env python3

import os
import time
import logging
import sys
import copy
import datetime
import ftpConn
import subprocess
import glob


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT,
                    #level=logging.INFO,
                    level=logging.DEBUG,
                    )

def initFtp():
    c = ftpConn.Creds()
    #wd = "htdocs/python_test/"
    wd = "/public_html/python_test"
    return ftpConn.ftpConn(c.host,c.user,c.passwd,wd)

def cleanupFtp():
    ftp = initFtp()
    ftpConn.rmOldFiles(ftp,limitSeconds=60*60*24*2)
    ftp.quit()

def rmfile(outfile):
    try:
        os.remove(outfile)
        logging.info("local rm %s" % outfile)
    except Exception as e:
        logging.error("rmfile() error: %s" % e)

def sendToFtp(outfiles):
    #postProc(outfile)
    ftp = initFtp()
    for f in outfiles:
        ftp.uploadFile(f)
        logging.info("sent to ftp %s" % f)
        rmfile(f)
    ftp.quit()

if __name__ == "__main__":
    mytime = int(time.time())
    L = list()
    for f in glob.glob('out/*'):
        ftime = os.path.getmtime(f)
        diff =  mytime - ftime
        if diff > 60*15:
            L.append(f)

    if L:
        sendToFtp(L)
