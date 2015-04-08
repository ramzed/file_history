import os
import shutil
import csv
import hashlib
import time
from datetime import datetime, timedelta
from daemon import Daemon

class Guarder(Daemon):
    """
    Basic class to control file state and save its history.
    History file format CSV
    """
    target_file = ''
    state_file = ''
    directory_for_save = ''
    min_period = 1

    def __init__(self, target_file, directory, state_file, min_period, log_file):
        super(Guarder, self).__init__('/tmp/file_history.pid', logfile=log_file)
        self.min_period = min_period
        self.target_file = target_file
        self.state_file = state_file
        file = open(self.state_file, 'w+')
        file.close()
        if directory.endswith('/'):
            self.directory_for_save = directory[:-1]
        else:
            self.directory_for_save = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def set_max_copies(self, count):
        self.max_copies = count

    def get_history(self):
        """
        This function is parsing csv file with history data. Returns a list of lists
        Format: [[datetime_string, md5sum, backup_file], [], ... []]
        """
        with open(self.state_file, 'rb') as csvfile:
            history = csv.reader(csvfile, delimiter=',')
            result = []
            for row in history:
                result.append(row)
        return result

    def check_target(self):
        """
        Check if current state is saved. Returns md5 hash if not saved. Returns False if saved.
        """
        hash = hashlib.md5(open(self.target_file, 'rb').read()).hexdigest()
        history = self.get_history()
        if len(history) == 0:
            return hash
        for line in history:
            if hash in line:
                return False
            else:
                continue
        return hash

    def get_last_savingdate(self):
        """
        Returns datetime of latest saving of target file
        """
        history = self.get_history()
        latest_date = datetime(1990,1,1)
        for line in history:
            if datetime.strptime(line[0],"%Y-%m-%d-%H-%M-%S") > latest_date:
                latest_date = datetime.strptime(line[0],"%Y-%m-%d-%H-%M-%S")
        return latest_date


    def save_state(self):
        try:
            curr_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            srcfile = self.target_file
            if self.target_file[:1] == '/':
                dstfile = self.directory_for_save + '/' + curr_time + '-' + self.target_file.split("/")[-1]
            else:
                dstfile = self.directory_for_save + '/' + curr_time + '-' + self.target_file
            self.logger.info("Copying " + srcfile + " to " + dstfile)
            shutil.copy(srcfile, dstfile)
        except Exception as e:
            self.logger.error(e)

        try:
            history = self.get_history()
        except Exception as e:
            self.logger.error(e)
        if len(history) >= self.max_copies:
            first_line = history.pop(0)
            try:
                os.remove(first_line[2])
            except:
                self.logger.error("Error was occured when deleting oldest backup")

            with open(self.state_file, 'wb') as csvfile:
                history2 = csv.writer(csvfile, delimiter=',')
                hash = hashlib.md5(open(self.target_file, 'rb').read()).hexdigest()
                for line in history:
                    history2.writerow(line)
                history2.writerow([curr_time, hash, dstfile])
            return

        with open(self.state_file, 'ab') as csvfile:
            history = csv.writer(csvfile, delimiter=',')
            hash = hashlib.md5(open(self.target_file, 'rb').read()).hexdigest()
            history.writerow([curr_time, hash, dstfile])

    def run(self):
        while True:
            time.sleep(1)
            try:
                if (datetime.now() - self.get_last_savingdate()) > timedelta(minutes=self.min_period):
                    if self.check_target():
                        self.save_state()
            except:
                self.logger.error("Error was occured in while loop")