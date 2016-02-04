# Little script for processing
# multiple Heegaard presentations
# at once, for the MOM project

import os

def twister_write(name,digested):
    sname = name + ".sur"
    os.system("touch " + sname)
    s = open(sname,'w')
    s.write(heegaard_to_twister(digested))
    s.close()
    tname = name + ".tri"
    command = "./Twister.out -f \"" + sname + "\" "
    command = command + "-s \"\" "
    handles = "-h \"a*b*c*"
    wds = digested[:2]
    handles = handles + wds[0] + "*" + wds[1] + "\" "
    command = command + handles
    command = command + "> " + tname
    os.system(command)
