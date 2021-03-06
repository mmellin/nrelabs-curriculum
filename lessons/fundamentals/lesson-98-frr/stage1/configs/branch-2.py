import paramiko
from glob import glob
import os
from scp import SCPClient

host=os.environ['SYRINGE_TARGET_HOST']

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

ssh=createSSHClient(host,22,"antidote","antidotepassword")

scp=SCPClient(ssh.get_transport())

#Change hostname

ssh.exec_command("sudo sed -E -i 's/^(127\.0\.1\.1\s+).*/\\1branch-2/' /etc/hosts")  
ssh.exec_command("sudo printf '%s' 'branch-2' > /etc/hostname") 
ssh.exec_command("sudo hostname branch-2")

#Copy configuration files over

ssh.exec_command('sudo cp /antidote/stage1/configs/branch-2/interfaces /etc/network/interfaces')
ssh.exec_command('sudo cp /antidote/stage1/configs/branch-2/daemons /etc/frr/daemons')
ssh.exec_command('sudo cp /antidote/stage1/configs/branch-2/*.conf /etc/frr')

ssh.exec_command('sudo chown frr:frr /etc/frr/*.conf')
ssh.exec_command('sudo chown frr:frrvty /etc/frr/vtysh.conf')
ssh.exec_command('sudo chmod 640 /etc/frr/*.conf')

#Restart FRR and bump interfaces
ssh.exec_command('sudo systemctl restart frr.service')
ssh.exec_command('sudo systemctl restart networking')

scp.close()
ssh.close()



