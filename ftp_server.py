'''
ftp 文件服务器
'''
from socket import *
import time
import os,sys
import signal

#文件库路径
file_path='/home/tarena/ftp/'
HOST = ''
PORT = 5000
ADDR = (HOST,PORT)

#将文件服务器功能写在类中
class FtpServer(object):
    def __init__(self,c):
        self.c=c
    def do_list(self):
        #获取文件列表
        file_list=os.listdir(file_path)
        if not file_list:
            self.c.send('文件库为空'.encode())
            return
        else:
            self.c.send(b'OK')
            time.sleep(0.1)
        files = ''
        for file in file_list:
            if file[0] != '.' and os.path.isfile(file_path+file):
                files=files+file+'#'
        self.c.sendall(files.encode())

    def do_get(self,filename):
        try:
            fd=open(file_path+filename,'rb')
        except:
            self.c.send('文件不存在'.encode())
            return
        self.c.send(b'OK')
        time.sleep(0.1)
        #发送文件
        while True:
            data=fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.c.send(b'##')
                break
            self.c.send(data)
        print('文件发送完毕')
        fd.close()

    def do_upload(self,filename):
        try: 
            fd=open(file_path+filename,'wb')
        except:
            self.c.send('文件上传失败'.encode())
            return
        self.c.send(b'OK')    
        while True:
            data=self.c.recv(1024)
            if data==b'##':
                break
            fd.write(data)
        fd.close()
        print('%s上传完毕'%filename)

#创建套接字，接收客户端连接，创建新的流程
def main():
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    #处理子进程退出
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    print('listen the port 5000...')

    while True:
        try:
            c,addr = sockfd.accept()
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit('服务器退出')
        except Exception as e:
            print('服务器异常:',e)
            continue
        print('已连接客户端：',addr)

        #创建子进程
        pid = os.fork()
        #子进程处理具体请求
        if pid == 0:
            sockfd.close()
            ftp=FtpServer(c)
            #判断客户请求
            while True:
                data=c.recv(1024).decode()
                if not data:
                    c.close()
                    sys.exit('客户端退出')
                elif data[0]=='L':
                    ftp.do_list()
                elif data[0]=='G':
                    filename=data.split(' ')[-1]
                    ftp.do_get(filename)
                elif data[0]=='U':
                    filename=data.split(' ')[-1]
                    ftp.do_upload(filename)
            
        #父进程或者创建失败，都继续等待下个客户端连接
        else:
            c.close()
            continue

if __name__ == '__main__':
    main()
