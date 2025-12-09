#!/usr/bin/env python3
# coding: utf-8 -*-
# @Author: aqwzj
# @Datetime : 2025/12/8 10:40
# @Project  : mayishenlin
# @File     : main.py.py
import cv2
import numpy as np
import uiautomator2 as u2
import time
import settings

class AntForestAutomation:
    def __init__(self):
        # 连接手机 (如果只连接了一台，可以使用默认连接)
        try:
            self.d = u2.connect()
            print(f"设备连接成功: {self.d.info.get('marketingName')}")
        except Exception as e:
            print(f"连接失败，请检查USB调试是否打开: {e}")
            exit()

        # ================= 配置区域 (请根据实际手机修改) =================

        # 变量1: 九宫格坐标 (格式: {数字: (x, y)})
        # 请通过"开发者选项"->"指针位置"获取你手机的具体坐标
        self.grid_coords = settings.grid_coords

        # 变量2: 密码顺序列表
        self.password_seq = settings.password_seq

        # ==============================================================

    def wake_and_unlock(self):
        """点亮屏幕并解锁"""
        print("正在唤醒屏幕...")
        self.d.screen_on()  # 点亮屏幕
        time.sleep(1)

        # 检查是否需要上滑显示密码盘 (很多手机亮屏后需要上滑)
        # 这里模拟一个从下往上的滑动
        w, h = self.d.window_size()
        self.d.swipe(w * 0.5, h * 0.9, w * 0.5, h * 0.4, 0.1)
        time.sleep(1)

        print(f"开始输入图案密码: {self.password_seq}")
        try:
            # 将数字序列转换为坐标列表
            points = [self.grid_coords[num] for num in self.password_seq]
            # 执行手势滑动，0.2秒完成
            self.d.swipe_points(points, 0.2)
            time.sleep(2)
            print("解锁完成")
        except Exception as e:
            print(f"解锁过程出错: {e}")

    def find_btn_coord(self, btn):
        """
        :param btn:
        find : 找能量按钮
        harvest: 一键收按钮
        :return: (x, y) coord or None
        """
        # 2. 配置参数（替换为你的模板图片路径）
        if btn not in ["find", "harvest"]:
            print(f"btn 参数错误, 预期值 find / harvest, 实际值 {btn}")
            return
        template_path = f"template/{btn}.png"

        threshold = 0.8  # 匹配阈值，0-1之间

        # 3. 截取屏幕并转换格式（PIL → OpenCV）
        screen = self.d.screenshot()  # 截取屏幕，返回PIL.Image对象
        screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)  # 转OpenCV格式

        # 4. 读取模板图片并匹配
        template = cv2.imread(template_path)
        h, w = template.shape[:2]
        result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # 5. 匹配成功则点击中心位置
        if max_val >= threshold:
            center_x = max_loc[0] + w / 2
            center_y = max_loc[1] + h / 2
            return center_x, center_y
        else:
            print(f"匹配失败，匹配值：{max_val} < 阈值：{threshold}")
            return

    def enter_ant_forest(self):
        """打开支付宝并进入蚂蚁森林"""
        print("启动支付宝...")
        self.d.app_start("com.eg.android.AlipayGphone")
        time.sleep(2)  # 等待启动

        # 尝试点击“蚂蚁森林”
        # 策略：先在首页找，找不到可能需要点击“全部”或者已经在森林里
        print("正在寻找蚂蚁森林入口...")

        # 如果当前不在森林界面，点击首页的图标
        if not self.d(text="种树").exists:
            forest_icon = self.d(text="蚂蚁森林")
            if forest_icon.exists:
                forest_icon.click()
            else:
                print("未在首页找到蚂蚁森林入口，请确保它在首页可见位置")
                return False

        time.sleep(2)  # 等待森林加载
        return True

    def collect_energy_loop(self):
        """循环收能量"""
        print("开始收集能量循环...")
        count = 0
        # 循环检查“找能量”按钮
        # 支付宝机制：点击“找能量”会跳转到好友森林，或者右上角有“找能量”跳转下一个
        while True:
            count += 1
            # 查找页面上是否有“找能量”按钮 (通常在右上角或者列表中)
            # 注意：不同版本支付宝文案可能不同，这里以“找能量”为例
            find_energy_btn = self.find_btn_coord(btn="find")

            if find_energy_btn:
                print(f"点击 '找能量' 跳转第 {count} 好友...")
                self.d.click(find_energy_btn[0], find_energy_btn[1])
                time.sleep(0.5)  # 等待进入好友页面

                # 检查是否有“一键收” (通常是背包道具) 或者直接点击能量球
                # 这里响应你的需求：点击“一键收”
                one_click_btn = self.find_btn_coord(btn="harvest")

                if one_click_btn:
                    print(f"发现 '一键收'，点击收取！")
                    self.d.click(one_click_btn[0], one_click_btn[1])
                    time.sleep(0.1)
                else:
                    # 如果没有一键收，可能需要手动点球（此处代码可扩展）
                    # 现在的版本通常会自动收，或者需要点击一个个球
                    # 简单处理：尝试点击明显的能量球（需要更复杂的图像识别，这里略过）
                    print("未发现一键收，跳过...")
            else:
                print("未找到 '找能量' 按钮，任务结束。")
                break

    def lock_screen(self):
        """锁屏"""
        self.d.app_stop("com.eg.android.AlipayGphone")
        print("执行锁屏...")
        # 回到桌面 (可选)
        self.d.press("home")
        time.sleep(1)
        # 关闭屏幕
        self.d.screen_off()

    def run(self):
        self.wake_and_unlock()
        if self.enter_ant_forest():
            self.collect_energy_loop()
        self.lock_screen()


if __name__ == "__main__":
    task = AntForestAutomation()
    task.run()

