from socket import *
from menu import show_menu
import sys
import time

#基本文件操作功能写在类里
class FtpClient(object):
    def __init__(self,sockfd):
        self.sockfd=sockfd

    def do_list(self):
        self.sockfd.send(b'L')#发送请求
        #等待回复
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            data = self.sockfd.recv(4096).decode()
            files = data.split('#')
            for file in files:
                print(file)
            print('文件列表展示完毕\n')
        else:
            #由服务器发送请求失败原因
            print(data)

    def do_get(self,filename):
        self.sockfd.send(('G '+filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            fd = open(filename,'wb')
            while True:
                data=self.sockfd.recv(1024)
                if data==b'##':
                    break
                fd.write(data)
            fd.close()
            print('%s下载完毕\n'%filename)
        else:
            print(data)

    def do_upload(self,filename):       
        try:
            fd=open(filename,'rb')
        except:
            print('文件打开失败')
            return
        self.sockfd.send(('U '+filename).encode())
        data=self.sockfd.recv(1024).decode()
        if data=='OK':
            while True:
                data=fd.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
            print('%s上传完毕'%filename)
        else:
            print(data)
       
#网络连接
def main():
    if len(sys.argv) < 3:
        print('argv is error')
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST,PORT)#文件服务器地址/服务端地址

    #创建套接字，跟服务端相同
    sockfd=socket()
    try:
        sockfd.connect(ADDR)
    except:
        print('连接服务器失败')
        return 

    ftp = FtpClient(sockfd) #功能类对象
    while True:
        show_menu()        
        cmd = input('请输入命令>>：')
        if not cmd:
            break
        elif cmd.strip()== '1' :
            ftp.do_list()
        elif cmd.strip()[0] =='2':
            filename=cmd.split(' ')[-1]
            ftp.do_get(filename)
        elif cmd.strip()[0]=='3':
            filename=cmd.split(' ')[-1]
            ftp.do_upload(filename)
        elif cmd.strip()[0]=='4':
            sys.exit(0)
        else:
            print('请输入正确命令！！！')
            continue

    # #关闭套接字
    # sockfd.close()

if __name__ == '__main__':
    main()