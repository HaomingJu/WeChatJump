# -*- coding:UTF-8 -*-
import os
import sys
import time
import cv2
import math
import random
import logging
import re


logging.basicConfig(level=logging.DEBUG, datefmt="%(asctime)s %(levelname)s ")



class WeChatJumpGame:
    # public:
    def __init__(self):
        self.k = 1
        self.m_img_h = -1
        self.m_img_w = -1
        self.img_rgb = None
        self.img_gray = None
        self.getScreenWH()
        self.rebootTimes = 0
        self.tryTimes = 0
        # print w, h in this function


        pass
    # 逻辑函数
    def Run(self):
        while True:                                                                 # 进入循环，不间断的刷分
            self.getScreenImage()                                                   # 获取图片
            if self.isReboot():                                                     # 判定是否一次刷分失败，如果失败自动进入下一次刷分
                self.touchRebootButton()                                            # 按下重新开始键
                continue                                                           # 直接进入下一个循环
            self.touchScreen(-1, -1, -1, -1, int(self.k * self.parseImage()))       # 分析图片，然后在一个随机位置按下特定时间
            time.sleep(random.uniform(2, 3.5))                                      # 暂停<随机数> 时间

    # private:
    def getScreenWH(self):
        cmd_getHW = "adb shell dumpsys window displays |head -n 10"                     # adb命令，获取屏幕分辨率
        pattern = re.compile("init=(?P<w>\d{3,4})x(?P<h>\d{3,4}).{1,}")                 # 正则表达式，找到分辨率的值
        r = os.popen(cmd_getHW)                                                         # 执行adb命令
        lines = r.readlines()
        for line in lines:
            match = pattern.search(line)
            if match is not None:
                self.m_img_w = int(match.group("w"))                              # 正则匹配到分辨率
                self.m_img_h = int(match.group("h"))
                logging.debug("Phone (w) = " + str(self.m_img_w) + " (h) = " + str(self.m_img_h))
                break
        return [self.m_img_w, self.m_img_h]

    def getScreenImage(self):
        cmd_imgCap = "adb shell screencap -p /sdcard/autojump.png"
        if (not os.path.exists("." + os.sep + "result" + os.sep + str(self.rebootTimes))):
            os.makedirs("." + os.sep + "result" + os.sep + str(self.rebootTimes), 0777)
        img_name = "." + os.sep + "result" + os.sep + str(self.rebootTimes) + os.sep + str(self.tryTimes) + ".png"
        cmd_pullImg = "adb pull /sdcard/autojump.png {img_name_}".format(img_name_=img_name)
        os.system(cmd_imgCap)
        os.system(cmd_pullImg)
        self.img_rgb = cv2.imread(img_name)

    def isReboot(self):
        roi_h = 10
        roi_w = 10
        roi_img = self.img_rgb[0:roi_h, 0:roi_w]
        Sum_0 = 0
        Sum_1 = 0
        Sum_2 = 0
        for i in range(roi_h):
            for j in range(roi_w):
                Sum_0 = Sum_0 + roi_img[i][j][0]
                Sum_1 = Sum_1 + roi_img[i][j][1]
                Sum_2 = Sum_2 + roi_img[i][j][2]
        rect = roi_w * roi_w
        Sum_0 = int(Sum_0 / rect)
        Sum_1 = int(Sum_1 / rect)
        Sum_2 = int(Sum_2 / rect)
        logging.debug("Sum_0 = {Sum0} Sum_1 = {Sum1} Sum_2 = {Sum2}".format(Sum0=Sum_0, Sum1=Sum_1, Sum2=Sum_2))
        if (45 <= Sum_0 <= 55) and (43 <= Sum_1 <= 50) and (40 <= Sum_2 <= 50):
            return True
        else:
            return False

    def touchRebootButton(self):
        logging.debug("touch reboot button")
        self.rebootTimes = self.rebootTimes + 1
        X1 = X2 = int(self.m_img_w / 2)
        Y1 = Y2 = int(self.m_img_h * 39 / 48)
        self.touchScreen(X1, Y1, X2, Y2, 10) # TODO 确定X1, Y1, X2, Y2
        time.sleep(random.uniform(3, 4))

    def touchScreen(self, x1_, y1_, x2_, y2_, during_):
        if x1_ == y1_ == x2_ == y2_ == -1:                                # 如果均为-1，则为随机数
            x1_ = int(random.uniform(0, self.m_img_w))
            y1_ = int(random.uniform(0, self.m_img_h))
            x2_ = int(random.uniform(0, self.m_img_w))
            y2_ = int(random.uniform(0, self.m_img_h))
        cmd_touchscreen = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
            x1=x1_,
            y1=y1_,
            x2=x2_,
            y2=y2_,
            duration=during_
        )
        logging.debug("touch ({x1}, {y1}) -> ({x2}, {y2}) for {dur}".format(x1=x1_, y1=y1_, x2=x2_, y2=y2_, dur=during_))
        os.system(cmd_touchscreen)
        self.tryTimes = self.tryTimes + 1

    def setK(self, k_):
        self.k = k_

    # 对图片进行分析
    def parseImage(self):
        # TODO 分析图片，
        distance = 0
        return distance # 返回两点图像间距离


    # 调试接口, **私用**
    def setImage(self, imgname):
        self.img_rgb = cv2.imread(str(imgname))
    

if __name__ == "__main__":
    obj = WeChatJumpGame()
    obj.setK(1)
    obj.Run()