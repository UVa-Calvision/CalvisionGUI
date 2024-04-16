from PyQt5.QtCore import *
import subprocess
import time
import sys
import os
import asyncio



class Worker_startDAQ(QObject):
    finished = pyqtSignal()
    # update_log_file_name = pyqtSignal(str)

    def __init__(self):
        super(Worker_startDAQ, self).__init__()
        # pipes = None



    def run(self):  
        # cmd_args = "/home/uva/calvision/CalvisionDaq/build/src/CalvisionDaq/exec/readout "
        cmd_args = "/home/uva/calvision/CalvisionDaq/data/config_file.txt "
        cmd_args += "test3.dat"
        print("DAQ started!")

        asyncio.run(self.run1(cmd_args))        
        
        
        self.finished.emit()

    async def run1(self,cmd_args):
        try:
            # pipes = await subprocess.Popen(cmd_args,stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,text=True)
            pipes = await asyncio.create_subprocess_exec("/home/uva/calvision/CalvisionDaq/build/src/CalvisionDaq/exec/readout","/home/uva/calvision/CalvisionDaq/data/config_file.txt","test3.dat",stdout=asyncio.subprocess.PIPE,stdin=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            std_out, std_err = await pipes.communicate()
            for line in std_out.decode("utf-8"):
            # for line in pipes.stdout:
                print(line) # process line here

            if pipes.returncode != 0:
                # an error happened!
                err_msg = "%s. Code: %s" % (pipes.stderr, pipes.returncode)
                raise Exception(err_msg)

            elif len(pipes.stderr):
                print(pipes.stderr)
                # return code is 0 (no error), but we may want to
                # do something with the info on std_err
                # i.e. logger.warning(std_err)
            else:
                pass
        except Exception as e:
            print(e)
        else:
            # print(std_out)
            pass


