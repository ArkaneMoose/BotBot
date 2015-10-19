from subprocess import call
from sys import executable, argv
from traceback import print_exc
from time import sleep

restart_delay_after_error = 10

def main():
    while True:
        try:
            if call([executable, '-m', 'botbot.main'] + argv[1:]) != 0:
                sleep(restart_delay_after_error)
        except:
            print_exc()
            sleep(restart_delay_after_error)

if __name__ == '__main__':
    main();
