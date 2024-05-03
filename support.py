from configparser import RawConfigParser
import requests

class Support:
    def __init__(self,filename):
        self.filename = filename
        self.config = RawConfigParser()
        self.config.read(self.filename)
    def read_config(self,section,option):
        return self.config.get(section,option)
    def write_config(self,section,option,value):
        self.config.set(section,option,value)
        with open(self.filename,"w") as f:
            self.config.write(f)
    def download_image(self,url, save_path):
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)