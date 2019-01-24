#  coding: utf-8 
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import socketserver
import datetime
import os
import mimetypes,urllib.request

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
                
        print("Connected to: ", self.client_address)
        #print ("Got a request of: %s\n" % self.data)
        req_type,path,version  = self.parse_req()
        print("PATH: " +path)
        if req_type== "GET":
            if path != "/favicon.ico":
                if self.check_traversal(path):
                    self.do_get(path)
                else:
                    error_resp = self.construct_headers("404 Not Found","text/html")
                    self.request.sendall(bytes(error_resp,"utf-8"))
                    return 1
            else:
                pass

        else:
            error_resp = self.construct_headers("405 Method Not Allowed","text/html")
            self.request.sendall(bytes(error_resp,"utf-8"))
            return 1

    def check_traversal(self,path):
        if path == "/":
            return True
        root = "/home/student/Desktop/404a1/CMPUT404-assignment-webserver/www/"
        if root in os.path.abspath(path):
            traversal =  os.path.exists(os.path.abspath(path))
            return traversal
        else:
            path= os.path.abspath(path)
            path = path[1:]
            full_path = root+path
            traversal = os.path.exists(full_path)
            return traversal

    def get_file(self,afile):
        #code to get mimetype obtained from users Gringo Suave and Navi StackOverflow on January 18 2019
        #https://stackoverflow.com/questions/14412211/get-the-mimetype-of-a-file-with-python

        url = urllib.request.pathname2url(afile)
        mtype= mimetypes.guess_type(url)[0]
        ok_resp = self.construct_headers("200 OK", mtype)
        f = open(afile,"r")
        ok_resp += f.read()
        self.request.sendall(bytes(ok_resp,"utf-8"))

    def do_get(self,path):
        if path == "/":
            ok_resp = self.construct_headers("200 OK", "text/html")
            index_file= open("index.html","r")
            ok_resp += index_file.read() 
            self.request.sendall(bytes(ok_resp,"utf-8"))
            return 1

        else:
            path = path[1:]
        if os.path.isfile(path):
            self.get_file(path)
            return 1

        if os.path.isdir(path):
            if not path.endswith("/"):
                new_path = "/"+path+"/"
                redirect_resp = self.construct_headers("301 Moved Permanently","text/html",new_path)
                #print(redirect_resp)
                self.request.sendall(bytes(redirect_resp,"utf-8"))
                return 1
            else:
                new_path = path+"index.html"
                self.get_file(new_path)
                return 1
        else:
            error_resp= self.construct_headers("404 Not Found","text/html")
            self.request.sendall(bytes(error_resp,"utf-8"))
            return 1

    def construct_headers(self,status,mimetype_header,location=None):
        status = "HTTP/1.1 {status}\r\n".format(status=status)
        date ="Date:  " + "{0:%Y-%m-%d %H:%M:%S}\r\n".format(datetime.datetime.now())
        
        mime_header = "Content-Type: "+ "{mime}\r\n".format(mime=mimetype_header)
        if location == None:
            response_header = status+mime_header+date+ "\r\n"
        
        else:
            location = "Location: "+location +"\r\n"
            response_header = status+location+mime_header+date+ "\r\n"

        return response_header
        
    def parse_req(self):
        self.data = self.request.recv(1024).strip()
        try:
            first_line = self.data.splitlines()[0]
            first_line = first_line.decode("utf-8")
            first_lines = first_line.rstrip('\r\n')
            (req_type,path,version) = first_line.split()
            attributes = (req_type,path,version)
            return attributes
        except IndexError:
            pass

if __name__ == "__main__":

    HOST, PORT = "localhost", 8080

    #Changing directory paths taken from user John Carter on January 15 2019
    #https://stackoverflow.com/questions/39801718/how-to-run-a-http-server-which-serve-a-specific-path


    www_dir = os.path.join(os.path.dirname(__file__), 'www')
    os.chdir(www_dir)

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
