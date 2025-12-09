#!/usr/bin/env python3
# coding: utf-8 -*-
# @Author: aqwzj
# @Datetime : 2025/12/8 10:40
# @Project  : mayishenlin
# @File     : main.py.py


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

    def enter_ant_forest(self):
        """打开支付宝并进入蚂蚁森林"""
        print("启动支付宝...")
        self.d.app_start("com.eg.android.AlipayGphone")
        time.sleep(5)  # 等待启动

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

        time.sleep(5)  # 等待森林加载
        return True

    def collect_energy_loop(self):
        """循环收能量"""
        print("开始收集能量循环...")

        # 循环检查“找能量”按钮
        # 支付宝机制：点击“找能量”会跳转到好友森林，或者右上角有“找能量”跳转下一个
        while True:
            # 查找页面上是否有“找能量”按钮 (通常在右上角或者列表中)
            # 注意：不同版本支付宝文案可能不同，这里以“找能量”为例
            find_energy_btn = self.d(text="找能量")

            if find_energy_btn.exists:
                print("点击 '找能量' 跳转下一位好友...")
                find_energy_btn.click()
                time.sleep(3)  # 等待进入好友页面

                # 检查是否有“一键收” (通常是背包道具) 或者直接点击能量球
                # 这里响应你的需求：点击“一键收”
                one_click_btn = self.d(text="一键收")

                if one_click_btn.exists:
                    print("发现 '一键收'，点击收取！")
                    one_click_btn.click()
                    time.sleep(2)
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

