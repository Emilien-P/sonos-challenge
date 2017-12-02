import src.Classifier as Cl
import cmd, readline, socket
import src.ModelWrapper as MW


def parse(arg):
    'Convert a series of zero or more argument to an argument tuple'
    return tuple(arg.split())

class MyServer():
    '''
    Very basic server to connect to the java frontend
    '''
    def __init__(self, arg=()):
        self.modelWrapper = MW.ModelWrapper(*arg)
        self.initialized = True
        self.sock = None

    def do_calibrate(self, arg):
        self.modelWrapper.calibrate(*arg)

    def do_compile(self, arg):
        self.modelWrapper.compile_model()

    def do_predict(self, arg):
        return self.modelWrapper.sample_and_predict()

if __name__ == "__main__":
    HOST = "192.168.1.2"
    PORT = 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    compiled = False
    buffersize = 1024
    serv = None

    while 1:
        try:
            str_input = sock.recv(buffersize).decode()
        except socket.herror:
            sock.sendall("ERROR IN SOCKET ADDRESS OR SETUP\n")
            break

        args = parse(str_input)
        command = str(args[0])
        args = args[1:]

        print(command)
        print(args)
        if command == "initialize":
            serv = MyServer(args)
        elif command == "calibrate":
            serv.do_calibrate(args)
        elif command == "listen":
            if not compiled:
                serv.do_compile(args)
                compiled = True
            name, command = serv.do_predict(args)
            sock.sendall((name + "/" + command + "\n").encode())
        elif command == "compile":
            serv.do_compile(args)
            sock.sendall(("OK" + "\n").encode())
        else:
            sock.sendall("WRONG COMMAND\n".encode())


