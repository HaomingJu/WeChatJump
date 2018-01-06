# -*- coding:UTF-8 -*-
import os
import sys
import time
import cv2
import math
import random
import logging
logging.basicConfig(level=logging.DEBUG)

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
        self.getScreenImage()                                                       # 获取宽高
        while True:                                                                 # 进入循环，不间断的刷分
            self.getScreenImage()                                                   # 获取图片
            if self.isReboot():                                                     # 判定是否一次刷分失败，如果失败自动进入下一次刷分
                self.touchRebootButton()                                            # 按下重新开始键
                continue                                                           # 直接进入下一个循环
            self.touchScreen(-1, -1, -1, -1, int(self.k * self.parseImage()))       # 分析图片，然后在一个随机位置按下特定时间
            time.sleep(random.uniform(2, 3.5))                                      # 暂停<随机数> 时间

    # private:
    def getScreenWH(self):
        # TODO 取得手机分辨率
        return [self.m_img_w, self.m_img_h]
        pass

    # 获取一帧图像
    def getScreenImage(self):
        cmd_imgCap = "adb shell screencap -p /sdcard/autojump.png"
        img_name = "." + os.sep + "result" + os.sep + str(self.rebootTimes) + os.sep + str(self.tryTimes) + ".png"
        cmd_pullImg = "adb pull /sdcard/autojump.png {img_name_}".format(img_name_=img_name)
        os.system(cmd_imgCap)
        os.system(cmd_pullImg)
        self.img_rgb = cv2.imread(img_name)

    def isReboot(self):
        # TODO 分析图片某个区间的颜色是否符合重启界面颜色
        pass

    # 按下重启键
    def touchRebootButton(self):
        self.rebootTimes = self.rebootTimes + 1
        self.touchScreen(X1, Y1, X2, Y2, 100) # TODO 确定X1, Y1, X2, Y2
        time.sleep(random.uniform(3, 4))

    # 按下某个区域并持续during时间
    def touchScreen(self, x1_, y1_, x2_, y2_, during_):
        if x1_ == y1_ == x2_ == y2_ == -1:                                # 如果均为-1，则为随机数
            x1_ = random.uniform(0, self.m_img_w)
            y1_ = random.uniform(0, self.m_img_h)
            x2_ = random.uniform(0, self.m_img_w)
            y2_ = random.uniform(0, self.m_img_h)
        cmd_touchscreen = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
            x1=x1_,
            y1=y1_,
            x2=x2_,
            y2=y2_,
            duration=during_
        )
        os.system(cmd_touchscreen)
        self.tryTimes = self.tryTimes + 1


    def setK(self, k_):
        self.k = k_

    # 对图片进行分析
    def parseImage(self):
        # TODO 分析图片，
        distance = 0
        return distance # 返回两点图像间距离

if __name__ == "__main__":
    obj = WeChatJumpGame()
    obj.setK(1)
    obj.Run()
    pass