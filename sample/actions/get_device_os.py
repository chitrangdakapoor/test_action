import re
import  paramiko
from paramiko_expect import SSHClientInteraction
from st2common.runners.base_action import Action

__all__ = [
    'GetDeviceOSAction'
]

class  GetDeviceOSAction(Action):
    def run(self, host, username, password):
        """
        The run function to login to a cisco and get the device OS.

        Arguments:
            host -- The IP Address of the device being checked
            username -- The username to connect
            password -- The password to connect
        Returns:
            JSON string with device OS and prompt
        """
        return self.get_device_os(host, username, password)

    def get_ssh_client(self, host, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username=username, password=password)
        except paramiko.AuthenticationException:
            result = {"logged_in": False, "details": "Authentication failed, please verify your credentials"}
            return False, result
        except paramiko.SSHException as sshException:
            result = {"logged_in": False, "details": "Unable to establish SSH connection: {}".format(sshException)}
            return False, result
        except paramiko.BadHostKeyException as badHostKeyException:
            result = {"logged_in": False,
                      "details": "Unable to verify server's host key: {}".format(badHostKeyException)}
            return False, result
        except Exception as e:
            result = {"logged_in": False, "details": e.args}
            return False, result
        return ssh

    def get_device_os(self, host, username, password):
        ssh_client = self.get_ssh_client(host, username, password)
        if isinstance(ssh_client, tuple):
            return ssh_client
        else:
            ssh = ssh_client

        prompt = self.get_device_prompt(host, username, password)
        stdin, stdout, stderr = ssh.exec_command("show version")
        if stdout:
            output = ""
            if not isinstance(stdout, str):
                output = (stdout.read()).decode("utf-8")
            else:
                output = stdout
            osInfo = re.search('(?:Cisco )(.*)(?: Software,)', output)
            osName = self.check_os(osInfo)
            if osName:
                result = {"os": osName,
                          "prompt": prompt,
                          "details": "Successfully got the device os"}
                return True, result
            else:
                result = {"os": "",
                          "prompt": "",
                          "details": "No os details were captured"}
                return False, result
        else:
            result = {"os": "",
                      "prompt": "",
                      "details": "Could not get device os---> {}".format((stderr.read()).decode("utf-8"))}
            return False, result

    def get_device_prompt(self, host, username, password):
        ssh_client = self.get_ssh_client(host, username, password)
        interact = SSHClientInteraction(ssh_client, timeout=10, display=True)
        interact.send("\n")
        interact.expect(".*")
        prompt = (str(interact.current_output)).strip()
        prompt_char = re.sub('[a-zA-Z0-9]*', '', prompt)
        return prompt_char

    def check_os(self, osInfo):
        if osInfo.group(1) and osInfo.group(1) == "IOS":
            return "IOS"
        elif osInfo.group(1) and osInfo.group(1) == "NX-OS":
            return "NX-OS"
        elif osInfo.group(1) and osInfo.group(1) == "CATOS":
            return "CATOS"
        else:
            return ""


