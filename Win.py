from myproject.mitm_start import mitmproxy_config, mitmproxy_start, mitmproxy_shutdown
from myproject.addons import Addon
from myproject.proxy_set import proxy_start, proxy_shutdown
from PyQt5.QtGui import QIcon
from configparser import ConfigParser
from subprocess import Popen
from PyQt5.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu, qApp, QAction, QDesktopWidget, QWidget
from sys import argv, exit


class SystemTray(object):
    # 程序托盘类
    def __init__(self, w, need_listen):
        self.app = app
        self.w = w
        self.need_listen = need_listen
        self.a1 = None
        self.mt, self.loop = None, None
        QApplication.setQuitOnLastWindowClosed(False)  # 禁止默认的closed方法，只能使用qapp.quit()的方法退出程序
        self.tp = QSystemTrayIcon(self.w)
        self.initUI()
        self.run()

    def initUI(self):
        # 设置托盘图标
        self.tp.setIcon(QIcon('myproject/ghost.ico'))

    def quitApp(self):
        # 退出程序
        re = QMessageBox.question(self.w, "提示", "退出并关闭代理", QMessageBox.Yes |
                                  QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            self.tp.setVisible(False)  # 隐藏托盘控件，托盘图标刷新不及时，提前隐藏
            self.close_mitmproxy()
            qApp.quit()  # 退出程序

    def act(self, reason):
        # 主界面显示方法
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            self.w.show()

    @staticmethod
    def message():
        # 提示信息被点击方法
        print("弹出的信息被点击了")

    def close_mitmproxy(self):
        mitmproxy_shutdown(self.mt)
        proxy_shutdown()
        self.a1.disconnect()
        self.a1.triggered.connect(self.start_mitmproxy)
        self.a1.setText('开启代理&(start)')

    def start_mitmproxy(self):
        if self.a1:
            self.a1.disconnect()
            self.a1.triggered.connect(self.close_mitmproxy)
            self.a1.setText('关闭代理&(start)')
        ip = "127.0.0.1"
        port = 9980
        # 启动代理
        proxy_start(ip, port)
        self.mt, self.loop = mitmproxy_config(ip, int(port), [Addon(self.need_listen)])
        # 启动mitmproxy代理
        mitmproxy_start(self.mt, self.loop)

    def run(self):
        self.start_mitmproxy()
        self.a1 = QAction('关闭代理&(start)')
        self.a1.triggered.connect(self.close_mitmproxy)
        a2 = QAction('&退出程序(Exit)', triggered=self.quitApp)
        tpMenu = QMenu()
        tpMenu.addAction(self.a1)
        tpMenu.addAction(a2)
        self.tp.setContextMenu(tpMenu)
        self.tp.show()  # 不调用show不会显示系统托盘消息，图标隐藏无法调用
        self.tp.showMessage('Hello', '解密代理已经启动了', icon=0)
        self.tp.messageClicked.connect(self.message)
        # 绑定托盘菜单点击事件
        self.tp.activated.connect(self.act)
        exit(self.app.exec_())  # 持续对app的连接


class Window(QWidget):
    # 主窗口类
    def __init__(self):
        # move()方法移动了窗口到屏幕坐标x=300, y=300的位置.
        super(Window, self).__init__()
        self._init()

    def _init(self):
        self.setWindowTitle('Test')  # 设置标题
        self.setWindowIcon(QIcon('./demo2.ico'))  # 设置标题图标
        self.resize(0, 0)  # 设置窗体大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        self.center()  # 窗体屏幕居中显示
        self.add_cert()

    def add_cert(self):
        conf = ConfigParser()
        conf.read("myproject/success.ini", encoding='utf-8')
        need_build = conf.getint("success", 'cert')
        need_listen = conf.get("host", "host_name")
        if not need_build:
            result = Popen(r'myproject/certmgr.exe -add -c "myproject/mitmproxy-ca-cert.p12" -s root').wait()
            if result:
                QMessageBox.information(self, "提示", "证书安装错误", QMessageBox.Yes)
                exit(-1)
            else:
                conf.set("success", "cert", "1")
                conf.write(open("myproject/success.ini", "r+", encoding="utf-8"))
                self.tray(need_listen)  # 程序实现托盘
        else:
            self.tray(need_listen)

    def tray(self, need_listen):
        # 创建托盘程序
        SystemTray(self, need_listen)

    def center(self):
        # 窗口居中方法
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    # 创建一个app程序
    app = QApplication(argv)
    # 创建窗口
    win = Window()
    exit(app.exec_())
