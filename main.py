
#!/usr/bin/python3
#coding=utf-8

from socket import *
from threading import Thread

HOST='localhost'
PORT=5550
BUFSIZE=1024
ADDR=(HOST,PORT)

Sock = socket(AF_INET,SOCK_STREAM)
Sock.bind(ADDR)
Sock.listen(5)
print("Server 127.0.0.1 listening...")

mydict=dict()
mylist=list()

##whatToSay send to all exceptNum
def tellOthers(mynum,whatToSay):
    for c in mylist:
        if c.fileno() != mynum:
            try:
                c.send(whatToSay.encode())
            except:
                pass

def subThreadIn(myconnection,connNumber):
    nickname = myconnection.recv(BUFSIZE).decode()
    mydict[myconnection.fileno()]=nickname
    mylist.append(myconnection)
    print('Connection',connNumber,'has nickname:',nickname)
    while True:
        try:
            recveMsg=myconnection.recv(BUFSIZE).decode()
            if not recveMsg:
                pass
            else:
                print(mydict[connNumber],':',recveMsg)
                tellOthers(connNumber,mydict[connNumber]+':'+recveMsg)
        except(OSError,ConnectionResetError):
            try:
                mylist.remove(myconnection)
            except:
                pass
            print(mydict[connNumber],'exit,',len(mylist),'person left')
            tellOthers(connNumber,'[Remind:'+mydict[connNumber]+' has left the chatting room]')
            myconnection.close()
            return

while True:
    connection,addr=Sock.accept()
    print('Accept a new connection',ADDR,connection.fileno())
    try:
        buf = connection.recv(BUFSIZE).decode()
        if buf == '1':
            connection.send(b'Welcome to server!')   ##Client端显示

            mythread = Thread(target=subThreadIn,args=(connection,connection.fileno()))
            mythread.setDaemon(True)
            mythread.start()
        else:
            connection.send(b'please go out!')
            connection.close()
    except:
        pass