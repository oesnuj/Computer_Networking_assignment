from socket import *
import sys
import os #캐시를 저장하기위한 폴더 관리르 위해 사용하는 라이브러리

if len(sys.argv) <= 1:
	print('Usage: "python ProxyServer.py server_ip port"\n[server_ip: IP Address Of Proxy Server, port: Port Number]')
	sys.exit(2)
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM) #TCP 서버소켓 생성
proxyPort = 8000 #포트번호 8000으로 지정
tcpSerSock.bind(("", proxyPort)) # 프록시 서버를 지정한 포트에 바인딩합니다.
print(proxyPort) #포트 확인을 위한 출력코드
tcpSerSock.listen(10) #최대 10개까지의 연결요청을 대기열에 둔다.
while 1:
	# Strat receiving data from the client
	print('Ready to serve...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('Received a connection from:', addr)
	message = tcpCliSock.recv(1024) #소켓으로부터 최대 1024byte의 데이터를 받아온다.
	message = message.decode() #소켓으로부터 받은 byte형태의 데이터를 문자열로 디코딩한다.
	print("message:", message)
	if(message == ''): #받은 메세지가 비어있을 경우를 무시하고 다음루프 진행 (예외처리, 유효성검사)
		continue
	# Extract the filename from the given message
	print("message.split()[1]:", message.split()[1])
	filename = message.split()[1].partition("/")[2]
	print("filename:", filename)

	if filename == 'favicon.ico': #
		print('favicon.ico request ignored.')
		# 파비콘 요청에 대해서는 빈 응답을 보내줌
		tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
		tcpCliSock.send("Content-Type:image/x-icon\r\n\r\n".encode())
		tcpCliSock.send(b'')
		continue
	fileExist = "false"
	filetouse = "/" + filename
	print("filetouse:", filetouse)
	try:
		# Check wether the file exist in the cache
		f = open("cache/" + filetouse[1:], "rb") #cache라는 폴더에서 클라이언트가 요청한 파일을 바이너리 읽기모드로 연다.
		outputdata = f.read()
		f.close()
		fileExist = "true"
		# ProxyServer finds a cache hit and generates a response message
		tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode()) #요청을 성곡적으로 처리하였다면 HTTP 응답코드 200 OK를 응답한다.
		tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode()) #응답 Content-Type을 text/html로지정하여 클라이언트에게 전송합니다.
		print('Read from cache') 
	# Error handling for file not found in cache
	except IOError:
		if fileExist == "false":
			# Create a socket on the proxyserver
			c = socket(AF_INET, SOCK_STREAM) #캐시폴더에 파일이 없기에 프록시 서버에 새로운 TCP 소켓을 생성핟나.
			hostn = filename.replace("www.","",1) #
			print("hostn:", hostn)
			try:
				# Connect to the socket to port 80
				serverName = hostn.partition("/")[0] #hostn에서 /이전부분을 serverName 변수에 저장한다.
				serverPort = 80 #포트번호를 80으로 설정한다.
				c.connect((serverName, serverPort)) #생성한 소켓을 사용하여 웹서버에 연결한다.
				askFile = ''.join(filename.partition('/')[1:]) #클라이언트가 요청한 파일에서 첫 번째 / 이후의 부분을 서버에게 요청할 파일로 설정한다.
				print("askFile:", askFile) #확인용 출력코드
				# Create a temporary file on this socket and ask port 80
				# for the file requested by the client
				fileobj = c.makefile('rwb', 0) # 새로 만든 소켓으로 파일을 요청할 때 사용할 임시 파일(fileobj)을 만든다.
				fileobj.write("GET ".encode() + askFile.encode() + " HTTP/1.0\r\nHost: ".encode() + serverName.encode() + "\r\n\r\n".encode()) 
				#서버에게 파일을 요청하는 HTTP GET 요청 메시지를 생성하고 서버에게 보냅니다.

				# Read the response into buffer
				serverResponse = fileobj.read()
				# Create a new file in the cache for the requested file.
				# Also send the response in the buffer to client socket and the corresponding file in the cache
				filename = "cache/" + filename #받아온 파일을 저장할 캐시 경로를 만든다. cache의 하위 디렉토리에 저장되게한다.
				filesplit = filename.split('/') #파일경로를 /로 나누어 리스트를 만든다.
				for i in range(0, len(filesplit) - 1): #파일의 경로에 해당하는 디렉토리들을 만드는 반복문입니다. 파일 이름 전까지 반복
					if not os.path.exists("/".join(filesplit[0:i+1])):
						os.makedirs("/".join(filesplit[0:i+1]))
				tmpFile = open(filename, "wb") #웹서버로 부터 받아온 파일을 저장할 임시파일(tmpFile)을 만든다.
				serverResponse = serverResponse.split(b'\r\n\r\n')[1] #서버로 부터 받은 응답에서 헤더를 \r\n\r\n를 기준으로 제외하고 본문 데이터만 받아온다.
				tmpFile.write(serverResponse) #바로위 코드의 본문 데이터를 tmpFile에 쓴다.
				tmpFile.close() #tmpFile 임시파일을 종룔한다.
				tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode()) #요청을 성공적으로 처리하였기에 HTTP 응답코드 200 OK를 응답한다.
				tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode()) #응답의 Content-Type을 text/html로 클라이언트에게 전송합니다.
				tcpCliSock.send(serverResponse) #서버응답 데이터를 클라이언트에게 전달한다.
			except:
				print("Illegal request") 
			c.close()
		else:
			# HTTP response message for file not found
			print("NET ERROR") #파일이 캐시에 없고, 서버에서도 찾을 수 없는 경우에 출력코드 작성
	# Close the client and the server sockets
	tcpCliSock.close()
tcpSerSock.close() # 서버소켓을 닫는다.