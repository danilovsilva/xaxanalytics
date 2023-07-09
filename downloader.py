import ftplib
import os
from passwd import userftp, passwdftp


class DownloadFTP():

    def download_demos(self, local_dest_path):
        # Connecting to the FTP server
        ftp = ftplib.FTP('ftp.maggie.hostzone.games')
        ftp.login(userftp, passwdftp)

        # Navigating to the directory where the .dem files are located
        ftp.cwd('/csgo/')

        # Listing the files in the directory
        files = ftp.nlst()

        # Choosing the destination folder where the files will be saved
        if not os.path.exists(local_dest_path):
            os.makedirs(local_dest_path)

        # Downloading the .dem files to the destination folder
        for file in files:
            # if file.endswith('.dem'):
            if file.endswith('.dem'):
                # Getting the file size
                file_size = ftp.size(file)

                # Checking if the file is greater than 50 MB (50 * 1024 * 1024 bytes)
                if file_size > 50 * 1024 * 1024:
                    if 'pug' in file:
                        # file_path = os.path.join(local_dest_path, file)
                        new_file_name = file
                    elif '_manual_map1_' in file:
                        name_date = file[0:13]
                        name_map = file[32:-4]
                        new_file_name = "get5pugren_"+name_map+"_"+name_date+".dem"

                        destination = '/csgo/' + new_file_name
                        ftp.rename(file, destination)
                        print("File " + file + " renamed to " +
                              new_file_name + " successfully.")

                    file_path = os.path.join(local_dest_path, new_file_name)

                    if not os.path.exists(file_path):
                        with open(file_path, 'wb') as f:
                            ftp.retrbinary('RETR ' + new_file_name, f.write)
                        print("File " + new_file_name +
                              " downloaded successfully.")

                        # Moving the .dem file to the '/csgo/demo_parsed' directory
                        destination = '/csgo/demo_parsed/' + new_file_name
                        ftp.rename(new_file_name, destination)
                        print("File " + new_file_name + " moved to " +
                              destination + " successfully.")

        # Closing the FTP connection
        ftp.quit()
