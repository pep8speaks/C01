import mimetypes
import string
import re 
import hashlib
from datetime import datetime
import requests
import time

import settings

PUNCTUATIONS = "[{}]".format(string.punctuation)

MAX_ATTEMPTS = 3
INTERVAL_BETWEEN_ATTEMPTS = 30

class DownloadRequest:
    def __init__(self, 
                url: str, 
                data_path: str, 
                crawler_id: str, 
                instance_id: str,
                referer: str, 
                filename: str = '', 
                filetype: str = '', 
                crawled_at_date: str = '') -> None:

        self.url = url
        self.crawler_id = crawler_id
        self.instance_id = instance_id
        self.referer = referer
        self.filetype = filetype if bool(filetype) else self.__detect_filetype()
        self.filename = filename if bool(filename) else self.__generate_filename()
        self.path_to_save = f'{data_path}/data/files/{self.filename}'
        self.data_path = data_path
        self.crawled_at_date = crawled_at_date


    def __generate_filename(self) -> str:        
        filename = hashlib.md5(self.url.encode()).hexdigest()
        filename += '.' + self.filetype if bool(self.filetype) else ''
        return filename

    def __filetype_from_url(self) -> str:
        """Detects the file type through its URL"""

        extension = self.url.split('.')[-1]
        if 0 < len(extension) < 6:
            return extension
        return ''

    def __filetype_from_filename_on_server(self, content_disposition: str) -> str:
        """Detects the file extension by its name on the server"""

        # content_disposition is a string with the following format: 'attachment; filename="filename.extension"'
        # the following operations are to extract only the extension
        extension = content_disposition.split(".")[-1]

        # removes any kind of accents
        return re.sub(PUNCTUATIONS, "", extension)

    def __filetype_from_mimetype(self, mimetype: str) -> str:
        """Detects the file type using its mimetype"""
        extensions = mimetypes.guess_all_extensions(mimetype)
        if len(extensions) > 0:
            return extensions[0].replace('.', '')

        return ''

    def __detect_filetype(self) -> str:
        """detects the file extension, using its mimetype, url or name on the server, if available"""
        filetype = self.__filetype_from_url()
        if len(filetype) > 0:
            return filetype

        response = requests.head(self.url, allow_redirects=True, headers=settings.REQUEST_HEADERS)
        
        content_type = response.headers.get("Content-type", "")
        content_disposition = response.headers.get("Content-Disposition", "")

        response.close()

        filetype = self.__filetype_from_filename_on_server(content_disposition)
        if len(filetype) > 0:
            return filetype

        self.__filetype_from_mimetype(content_type)
    
    def __notify_server(self, message: str):
        server_notification_url = f'http://localhost:9000/download/file/{message}/{self.instance_id}' 
        req = requests.get(server_notification_url)
        
        if req.status_code == 200:
            print('Server notified...')

        else:
            print('Error notifying server...')

    def __notify_server_successful_download(self):
        self.__notify_server('success')

    def __notify_server_error_dowload(self):
        self.__notify_server('error')

    def exec_download(self) -> bool:
        print(f"Downloading {self.url}")
        
        attempt = 0
        while attempt < MAX_ATTEMPTS:
            with requests.get(self.url, stream=True, allow_redirects=True, headers=settings.REQUEST_HEADERS) as req:
                if req.status_code != 200:
                    attempt += 1
                    time.sleep(attempt * INTERVAL_BETWEEN_ATTEMPTS)
                    continue

                with open(self.path_to_save, "wb") as f:
                    for chunk in req.iter_content(chunk_size=8192):
                        f.write(chunk)
                    break 
                
        if attempt == MAX_ATTEMPTS:
            self.__notify_server_error_dowload()
            return False 

        else:
            self.crawled_at_date = str(datetime.today())
            self.__notify_server_successful_download()
            return True

    def get_description(self) -> dict:
        return {
            'url': self.url,
            'data_path': self.data_path,
            'relative_path': self.path_to_save,
            'crawler_id': self.crawler_id,
            'instance_id': self.instance_id,
            'referer': self.referer,
            'file_name': self.filename,
            'type': self.filetype,
            'crawled_at_date': self.crawled_at_date,
            'extracted_files': [

            ]
        }