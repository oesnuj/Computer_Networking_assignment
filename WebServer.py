#import socket module
from socket import *
import sys # In order to terminate the program

serverSocket = socket(AF_INET, SOCK_STREAM)
#Prepare a sever socket

#Fill in start
serverPort = 8000 #서버포트번호를 8000으로 지정한다.
serverSocket.bind(('', serverPort)) #서버소켓을 모든 네트워크인터페이스에 8000번 포트로 바인딩한다.
serverSocket.listen(1) #클라이언트의 접속이 올때까지 기달리는 중이다.
#Fill in end
# ...
while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept() 
    #클라이언트가 연결되면 connection이라는 소켓을 새로 생성하고 클라이언트 정보를 addr에 저장한다. 
    #Fill in start   #Fill in end
    try:
        message =  connectionSocket.recv(1024)
        #클라이언트로부터 최대 1024byte 크기의 데이터를 받는다
        #Fill in start          #Fill in end
        filename = message.split()[1]
        #HTTP 요청 메시지에서 요청된 파일의 이름을 추출합니다.
        #f = open(filename[1:])
        f = open(filename[1:], 'r', encoding='utf-8')
        #요청된 파일을 서버 시스템에서 오픈한다.
        outputdata = f.read() #위 코드에서 연 파일 내용을 outputdata 변수에 저장한다.
        #Fill in start       #Fill in end
        #Send one HTTP header line into socket
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        # 클라이언트에게 200 OK 응답을 보냅니다.
        #Fill in end
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):           
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        
        connectionSocket.close()
    except IOError:
        #Send response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        #파일이 존재하지 않거나 열리지 않는 경우 클라이언트에게 404 Not Found 응답을 보냅니다.
        #Fill in end
        #Close client socket
        connectionSocket.close() #클라이언트와 연결을 종료한다.
          
serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data