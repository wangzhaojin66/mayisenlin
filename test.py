import uiautomator2 as u2

d = u2.connect()  # USB 调试
# d = u2.connect("172.16.20.66:5555")  # WIFI连接调试
if d.info['screenOn']:
    print("亮屏")
else:
    print("息屏")

