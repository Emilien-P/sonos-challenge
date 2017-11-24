import src.Classifier as Cl
import cmd, readline
import src.ModelWrapper as MW


class sonosShell(cmd.Cmd):
    nb_sample = 0
    modelWrapper = None
    initialized = False

    def do_initialize_model(self, arg):
        self.modelWrapper = MW.ModelWrapper(*parse(arg))
        self.initialized = True

    def do_calibrate(self, arg):
        self.modelWrapper.calibrate(*parse(arg))

    def do_compile(self):
        self.modelWrapper.compile_model()

    def predict(self):
        print(self.modelWrapper.sample_and_predict())

def parse(arg):
    'Convert a series of zero or more argument to an argument tuple'
    return tuple(arg.split())

if __name__ == '__main__':
    '''
    Command line approach to share data between the sonos front-end and the python ML models.
    '''
    sonosShell().cmdloop()

