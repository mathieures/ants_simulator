import commands
commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]


"""
import subprocess
cmd = "ifconfig | grep 255.255.255.0"
inet = subprocess.check_output(cmd, shell=True).decode()
inet = inet.split(" ")
inet_addr = inet[inet.index("inet")+1]
print(inet_addr)
"""
