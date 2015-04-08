import sys, time
import ConfigParser
from guarder import Guarder

try:
    config = ConfigParser.RawConfigParser()
    config.read('/etc/file_history.conf')

    target_file = config.get("main", "target_file")
    saving_directory = config.get("main", "backup_directory")
    state_file = config.get("main", "state_file")
    min_saving_period = config.getint("main", "min_saving_period")
    max_copies = config.getint("main", "max_copies")
    log_file = config.get("main", "log_file")

except:
    print "Fatal error: error when trying to parse config file..."
    exit(1)

if __name__ == "__main__":
    daemon = Guarder(target_file, saving_directory, state_file, min_saving_period, log_file)
    daemon.set_max_copies(max_copies)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)