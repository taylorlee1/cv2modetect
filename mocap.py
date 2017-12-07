#! /usr/bin/env python3

import numpy as np
import cv2
import os
import time
import argparse
import logging
import sys
import copy
import imutils
import datetime
import threading
import ftpConn
import queue
import subprocess
from collections import deque

MOTION_FRAME_WIDTH = 300
FPS=30.0

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT,
                    #level=logging.INFO,
                    level=logging.DEBUG,
                    )

def parseArgs():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--resolution", \
            help="resolution of result vids WxH",
            default='960x720')
    ap.add_argument("-a", "--min-area-percent", type=float, \
            default=5, help="min area size in percentage",
            dest='minAreaPercent')
    ap.add_argument("-p", "--pre-frames", type=int, \
            default=100, dest='preframes',
            help="prior non motion frames to keep")


    args = vars(ap.parse_args())
    try:
        reso = args['resolution'].split('x')
    except Exception as e:
        reso = '960x720'
    try:
        args['w'] = int(reso[0])
    except Exception as e:
        args['w'] = 960
    try:
        args['h'] = int(reso[1])
    except Exception as e:
        args['h'] = 720

    scalar = float(MOTION_FRAME_WIDTH) / args['w'];
    logging.debug("w,h %d,%d" % (args['w'],args['h']))
    bigarea = args['w'] * args['h']
    smallarea = float(bigarea) * scalar * scalar
    args['areaThresh'] = float(args['minAreaPercent'])/100 * \
                        smallarea
    logging.debug("bigarea: %d" % (bigarea))
    logging.debug("scalar: %.3f" % (scalar))
    logging.debug("smallarea: %d" % (smallarea))
    logging.debug("areaThresh: %d" % (args['areaThresh']))
    
    return args

def setWidthHeight(cap,w,h):
    wprop=cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
    hprop=cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

def getWidthHeight(cap):
    w=cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    logging.debug("cap w,h %d,%d" % (w,h))
    return w,h

def setupCaptureDevice(args):

    for i in range(-1,40):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            logging.info("device %d opened" % (i))
            setWidthHeight(cap, args['w'], args['h'])
            w,h = getWidthHeight(cap)
            args['h'] = h
            args['w'] = w
            time.sleep(5)
            return cap
        else:
            logging.info("device %d not opened" % i)

    return None

def genMotionFrame(rawFrame):
    motionFrame = imutils.resize(rawFrame, width=MOTION_FRAME_WIDTH)
    motionFrame = cv2.cvtColor(motionFrame, 
            cv2.COLOR_BGR2GRAY)
    motionFrame = cv2.GaussianBlur(motionFrame, 
            (21,21), 0)
    #logging.debug("motion frame size: %d %d" % (
    #    motionFrame.shape[0],
    #    motionFrame.shape[1]))
    
    return motionFrame

def detectMotion(motionFrameFirst,
        motionFrame,
        areaThresh):

    motionFrame = cv2.absdiff(motionFrameFirst,
            motionFrame) # simple diff

    motionFrame = cv2.threshold(motionFrame, 25, 255,
            cv2.THRESH_BINARY)[1] # make B/W

    numberMotionBlocks = cv2.countNonZero(motionFrame)
    if numberMotionBlocks > areaThresh:
        logging.info("OK %d > %d" % (
            numberMotionBlocks,
            areaThresh,
            ))
        return True
    else:
        #logging.debug("KO %d < %d" % (
        #    numberMotionBlocks,
        #    areaThresh,
        #    ))
        return False

def getTimeStamp():
    return datetime.datetime.now().strftime( \
        "%Y.%m.%d.%H.%M.%S"),

def addText(f):
    now = getTimeStamp()
    try:
        cv2.putText(f, str(now), (10,f.shape[0]-10), \
            cv2.FONT_HERSHEY_PLAIN, 1.0, \
            (255,255,255), 1)
    except Exception as e:
        logging.error("addtext error: %s" % (e))
    return f

def keepCapturing(firstFrame, cap):
    M = deque([firstFrame], maxlen=5)
    S = deque(maxlen=120)
    L = list()
    while True:
        (retval, rawFrame) = cap.read()
        if not retval:
            logging.warning("cap.read() error: %s" % (e))
            time.sleep(1)
            continue

        motionFrame = genMotionFrame(rawFrame)

        S.append(detectMotion(M[0], motionFrame, 0))
        #logging.debug("sum S: %d" % (sum(S)))
        
        if sum(S) > 0:
            L.append(addText(rawFrame))
            M.append(motionFrame)
        else:
            break

        if len(L) > 300:
            logging.warning("Buffer over 300!")
            break

    return L

def initFtp():
    c = ftpConn.Creds()
    #wd = "htdocs/python_test/"
    wd = "/public_html/python_test"
    return ftpConn.ftpConn(c.host,c.user,c.passwd,wd)

def cleanupFtp():
    ftp = initFtp()
    ftpConn.rmOldFiles(ftp,limitSeconds=60*60*24*2)
    ftp.quit()

def postProc(outfile):
    proc = subprocess.Popen(['./postproc.sh', outfile], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
    stdout,stderr = proc.communicate()
    try:
        for line in stdout.decode('utf8').split('\n'):
            logging.debug("postProc() stdout: %s" % line.strip())
        for line in stderr.decode('utf8').split('\n'):
            logging.debug("postProc() stderr: %s" % line.strip())
    except Exception as e:
        logging.warning("postProc() error: %s" % e)

def rmfile(outfile):
    try:
        os.remove(outfile)
        logging.info("local rm %s" % outfile)
    except Exception as e:
        logging.error("rmfile() error: %s" % e)

def sendToFtp(outfile):
    #postProc(outfile)
    ftp = initFtp()
    ftp.uploadFile(outfile)
    logging.info("sent to ftp %s" % outfile)
    rmfile(outfile)
    ftp.quit()

def writeOut(writeQ):
    while True:
        D = writeQ.get()
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        now = getTimeStamp()
        outfile = 'out/output.%s.mp4' % (now)
        w = D[0].shape[1]
        h = D[0].shape[0]
        logging.debug("out file size: %d %d %d" % (w,h,D[0].size))
        out = cv2.VideoWriter(outfile ,fourcc, FPS, (w,h))
        logging.debug("size of deque %d" % len(D))
        for f in D:
            out.write(f)
            #logging.debug("frame size %d %d %d" % (
            #        f.shape[1],
            #        f.shape[0],
            #        f.size,))
        out.release()
        logging.info("wrote %s" % (outfile))
        try:
            sendToFtp(outfile)
        except Exception as e:
            logging.error("sendToFtp error: %s" % e)
        finally:
            logging.debug("sendToFtp() done")

        try:
            cleanupFtp()
        except Exception as e:
            logging.error("cleanupFtp error: %s" % e)
        finally:
            logging.debug("cleanupFtp() done")


def motion(cap, args, writeQ):
    motionFrameFirst = []
    DRaw = deque(maxlen=args['preframes'])
    logging.debug("main deque size: %d" % len(DRaw))

    while True:
        (retval, rawFrame) = cap.read()
        DRaw.append(addText(rawFrame))

        if not retval:
            logging.warning("cap.read() error: %s" % (e))
            time.sleep(1)
            continue

        motionFrame = genMotionFrame(rawFrame)

        if len(motionFrameFirst) == 0:
            motionFrameFirst.append(motionFrame)
            continue
        
        motionDetected = detectMotion(motionFrameFirst[0],
                            motionFrame,
                            args['areaThresh'])

        if motionDetected:
            RawFrames = keepCapturing(motionFrameFirst[0], cap)
            #DRaw.extend(RawFrames)

            try:
                writeQ.put(deque(list(DRaw) + list(RawFrames)))
            except Exception as e:
                logging.error("Could not put onto writeQ: %s"  % e)
            #d = threading.Thread(target=writeOut, 
            #        args=(copy.deepcopy(DRaw),),
            #        daemon=True)
            #d.daemon = True
            #d.start()

            DRaw.clear()
            motionFrameFirst = list()

def turnOffAutoFocus():
    time.sleep(360)
    proc = subprocess.Popen("uvcdynctrl -v --set='Focus, Auto' 0", 
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE
         )

    stdout,stderr = proc.communicate()
    logging.info("turnOffAutoFocus() stdout: %s" % stdout)
    logging.info("turnOffAutoFocus() stdout: %s" % stderr)

    proc = subprocess.Popen("uvcdynctrl -v --get='Focus, Auto'", 
            stdout=subproces.PIPE,
            stderr=subprocess.PIPE
            )

    stdout,stderr = proc.communicate()
    logging.info("turnOffAutoFocus() stdout: %s" % stdout)
    logging.info("turnOffAutoFocus() stdout: %s" % stderr)


    #uvcdynctrl -v -d video0 --set='Focus (absolute)' 0
    proc = subprocess.Popen("uvcdynctrl -v --set='Focus (absolute)' 0", 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )

    stdout,stderr = proc.communicate()
    logging.info("turnOffAutoFocus() stdout: %s" % stdout)
    logging.info("turnOffAutoFocus() stdout: %s" % stderr)

    proc = subprocess.Popen("uvcdynctrl -v --get='Focus (absolute)'", 
            stdout=subproces.PIPE,
            stderr=subprocess.PIPE
            )

    stdout,stderr = proc.communicate()
    logging.info("turnOffAutoFocus() stdout: %s" % stdout)
    logging.info("turnOffAutoFocus() stdout: %s" % stderr)


            
if __name__ == "__main__":
    writeQ = queue.Queue()
    args = parseArgs()
    cap = setupCaptureDevice(args)
    if not cap:
        logging.error("no capture device could be open")
        sys.exit(5)

    threading.Thread(target=writeOut,
                    args=(writeQ,),
                    daemon=True).start()

    threading.Thread(target=turnOffAutoFocus,
                    daemon=True).start()
    
    motion(cap, args, writeQ)

