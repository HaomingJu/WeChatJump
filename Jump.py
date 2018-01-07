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
        self.line_0 = 0
        self.line_1 = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.body_w = 76                # 小棋子宽度
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
            time.sleep(random.uniform(1, 2))                                      # 暂停<随机数> 时间

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
        self.line_0 = int(self.m_img_h * 17 / 96)
        self.line_1 = int(self.m_img_h * 39 / 48)
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
        self.tryTimes = 0
        X1 = X2 = int(self.m_img_w / 2)
        Y1 = Y2 = self.line_1
        self.touchScreen(X1, Y1, X2, Y2, 10) # TODO 确定X1, Y1, X2, Y2
        time.sleep(random.uniform(3, 4))

    def touchScreen(self, x1_, y1_, x2_, y2_, during_):
        if x1_ == y1_ == x2_ == y2_ == -1:                                # 如果均为-1，则为随机数
            x1_ = int(random.uniform(self.m_img_w /2 - 10, self.m_img_w /2 + 10))
            y1_ = int(random.uniform(self.line_1 - 10, self.line_1 + 10))
            x2_ = int(random.uniform(self.m_img_w /2 - 10, self.m_img_w /2 + 10))
            y2_ = int(random.uniform(self.line_1 - 10, self.line_1 + 10))
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
        distance = 0
        start_ = self.findStart()
        end_ = self.findEnd()
        return self.calDistance(start_, end_)     # 返回两点图像间距离

    # 找到起点
    def findStart(self):
        _0 = []
        _1 = []
        _2 = []
        for i in range(self.line_1, self.line_0, -3):
            for j in range(0, self.m_img_w - 50):
                Sum_0 = 0
                Sum_1 = 0
                Sum_2 = 0
                length = 20
                for n in range(0, length, 1):
                    Sum_0 = Sum_0 + self.img_rgb[i][j+n][0]
                    Sum_1 = Sum_1 + self.img_rgb[i][j+n][1]
                    Sum_2 = Sum_2 + self.img_rgb[i][j+n][2]
                Sum_0 = int(Sum_0 / length)
                Sum_1 = int(Sum_1 / length)
                Sum_2 = int(Sum_2 / length)
                if (95 <= Sum_0 <= 105) and (50 <= Sum_1 <= 60) and (50 <=Sum_2 <= 60):
                    logging.info("find start: ({x}, {y})".format(x=j+20, y=i))
                    self.x1 = j+20
                    self.y1 = i
                    return [self.x1, self.y1]
        self.x1 = 0
        self.y1 = 0
        return [0,0]
            
    # 找到终点
    def findEnd(self):
        self.drawBK()
        for i in range(self.line_0, self.line_1, 3):
            for j in range(0, self.m_img_w - 50, 2):
                Sum_0 = 0
                Sum_1 = 0
                length = 4
                for n in range(0, length, 1):
                    Sum_0 = Sum_0 + self.img_rgb[i][j+n][0] + self.img_rgb[i][j+n][1] + self.img_rgb[i][j+n][2]
                    Sum_1 = Sum_1 + self.img_rgb[i][j+n+length][0] + self.img_rgb[i][j+n+length][1] + self.img_rgb[i][j+n+length][2]
                    Sum_0 = Sum_0 / length
                    Sum_1 = Sum_1 / length
                if ((abs(Sum_1 - Sum_0) > 30) or (Sum_1 >= 243)) and (abs(j - self.x1) > self.body_w):
                    logging.info("find end: ({x}, {y})".format(x=j+20, y=i))
                    self.x2 = j+20
                    self.y2 = i
                    return [j+20, i]
        self.x2 = 0
        self.y2 = 0
        return [0, 0]
    
    def drawBK(self):
        Sum_bk = 0
        for j in range(0, self.m_img_w, 1):
            Sum_bk = Sum_bk + self.img_rgb[self.line_0, j][0] + self.img_rgb[self.line_0, j][1] + self.img_rgb[self.line_0, j][2]
        Sum_bk = Sum_bk / self.m_img_w

        for p in range(self.line_0, self.line_1, 1):
            for q in range(0, self.m_img_w, 1):
                Sum = 0
                Sum = Sum + self.img_rgb[p, q][0] + self.img_rgb[p, q][1] + self.img_rgb[p, q][2]
                if abs(Sum - Sum_bk) > 40:
                    self.img_rgb[p, q] = [0, 0, 0]
        # self.img_rgb = cv2.resize(self.img_rgb, (int(self.m_img_w / 2), int(self.m_img_h / 2)))
        # cv2.imshow("win", self.img_rgb)
        # cv2.waitKey(-1)


                    


    # 返回两点间距离
    def calDistance(self, start_, end_):
        x1 = start_[0]
        y1 = start_[1]
        x2 = end_[0]
        y2 = end_[1]
        return math.sqrt(pow(abs(x1 - x2), 2) + pow(abs(y1 - y2), 2))



    # 调试接口, **私用**
    def setImage(self, imgname):
        self.img_rgb = cv2.imread(str(imgname))
    def drawCircle(self, x, y):
        cv2.circle(self.img_rgb, (x, y), 5, (0, 0, 255), 8)
    def showImage(self):
        self.img_rgb = cv2.resize(self.img_rgb, (int(self.m_img_w / 2), int(self.m_img_h / 2)))
        cv2.imshow("win", self.img_rgb)
        cv2.waitKey(-1)
    

if __name__ == "__main__":
    obj = WeChatJumpGame()
    
    # obj.setImage("./result/1/50.png")
    # [x, y] = obj.findEnd()
    # obj.drawCircle(x, y)
    # obj.showImage()
    
    obj.setK(1.25)
    obj.Run()