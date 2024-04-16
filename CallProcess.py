import subprocess
import sys
import os


# Helper class for calling processes and communicating data between them
# Run can be called multiple times (makes new process internally)
class CallProcess:
    def __init__(self):
        pass

    # Runs the process and prints the stdout and stderr
    # This is blocking, but you may call message and other methods
    # from other threads while it's running
    def run(self, command):
        try:
            self.proc = subprocess.Popen(command,
                                         stdin = subprocess.PIPE,
                                         stdout = subprocess.PIPE,
                                         stderr = subprocess.PIPE,
                                         shell = True,
                                         text = True)

            # Readout lines from os file handle. Print them by newline like usual
            self.print_lines_from_fd(self.proc.stdout.fileno(), handle=True )
            self.print_lines_from_fd(self.proc.stderr.fileno(), handle=False)
            
            # Wait for the process to end (pipes might close before process stops)
            self.proc.wait()

            # Check return code
            if self.proc.returncode != 0:
                raise Exception("Command Error {}".format(self.proc.returncode))
        except Exception as e:
            print(e)

    # Check if the process has started and is running
    def running(self):
        if self.proc == None: return False
        return self.proc.poll() == None

    def message(self, text):
        # Check if proc is running
        if not self.running():
            print("Process isn't running. Can't send text: {}".format(text))
            return

        # Send text through stdin
        os.write(self.proc.stdin.fileno(), text.encode('utf-8'))

    def print_lines_from_fd(self, fd, handle=True):
        s = ""
        while True: 
            new_text = os.read(fd, 10).decode('ascii')
            if len(new_text) == 0:
                for line in s.splitlines():
                    if handle:
                        self.handle_output(line)
                    else:
                        print(line)
                break

            s += new_text
            lines = s.splitlines()
            if s[-1] != '\n':
                s = lines[-1]
                lines.pop()
            else:
                s = ""
            for line in lines:
                if handle:
                    self.handle_output(line)
                else:
                    print(line)


    # Helper function for how to handle output
    def handle_output(self, line):
        pass


# Call Raspberry Pi client with verbose output
# Generally this won't look at returned data from the Pi
class ClientVerboseProcess(CallProcess):
    def __init__(self):
        pass

    def handle_output(self, line):
        print(line)

    def run(self, ip_address, port, command):
        CallProcess.run(self, "/home/uva/local_install/bin/client {} {} -c '{}'".format(ip_address, port, command))


# Call Rasperry Pi client and supress its output. Sets self.result
# to the returned data from the Pi if available (None otherwise)
class ClientReadProcess(CallProcess):
    def __init__(self):
        self.result = None

    def handle_output(self, line):
        self.result = line

    def run(self, ip_address, port, command):
        CallProcess.run(self, "/home/uva/local_install/bin/client {} {} -b '{}'".format(ip_address, port, command))

    # Static method for quickly calling the process and getting the result
    def execute(ip_address, port, command):
        proc = CallProcess()
        proc.run(ip_address, port, command)
        return proc.result

