import json
import platform
import os


class ModuleLoader:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"模板文件未找到: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def build_command(self, params):
        system = platform.system().lower()
        if system == "windows":
            key = "windows"
        elif system == "darwin":
            key = "mac"
        else:
            key = "linux"

        if key not in self.data["platforms"]:
            raise KeyError(f"不支持的平台: {key}")
            
        template = self.data["platforms"][key]["command"]
        for k, v in params.items():
            template = template.replace("{" + k + "}", v)
        return template