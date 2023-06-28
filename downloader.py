import ftplib
import os
from passwd import userftp, passwdftp


class DownloadFTP():

    def download_demos(self, path):
        # Connecting to the FTP server
        ftp = ftplib.FTP('ftp.maggie.hostzone.games')
        ftp.login(userftp, passwdftp)

        # Navigating to the directory where the .dem files are located
        ftp.cwd('/csgo/')

        # Listing the files in the directory
        files = ftp.nlst()

        # Choosing the destination folder where the files will be saved
        if not os.path.exists(path):
            os.makedirs(path)

        # Downloading the .dem files to the destination folder
        for file in files:
            if file.endswith('.dem'):
                file_path = os.path.join(path, file)
                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        ftp.retrbinary('RETR ' + file, f.write)
                    print("File " + file + " downloaded successfully.")

                    # Moving the .dem file to the '/csgo/demo_parsed' directory
                    destination = '/csgo/demo_parsed/' + file
                    ftp.rename(file, destination)
                    print("File " + file + " moved to " +
                          destination + " successfully.")

        # Closing the FTP connection
        ftp.quit()
