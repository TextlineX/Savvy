import subprocess

class Executor:
    def run(self, command_str):
        result = subprocess.run(command_str, shell=True,
                                capture_output=True, text=True)
        return result.stdout, result.stderr