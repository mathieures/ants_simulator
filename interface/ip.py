import commands
commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
