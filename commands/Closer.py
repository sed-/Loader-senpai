import os
import psutil
import logging
from time import sleep
from colorama import init, Fore

class Closer:
    requires_api = False
    requires_parameter = False
    requires_username = False
    def __init__(self, processes=None, file_path='closeall.ini'):
        init()
        self.file_path = file_path
        self.processes = processes or ['agent.exe', 'Battle.net.exe', 'overwatch.exe', 'HeroesOfTheStorm_x64.exe', 'steam.exe', 'brave.exe', 'discord.exe', 'msedge.exe']
        self.load_processes()

    def load_processes(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                for process in self.processes:
                    f.write(f"{process}\n")
        else:
            self.processes = self.get_processes_from_file(self.file_path)

    @staticmethod
    def get_processes_from_file(file_path):
        with open(file_path, 'r') as f:
            return {line.strip(): None for line in f}

    @staticmethod
    def print_header():
        print(Fore.LIGHTBLACK_EX + '|-|-|-|-|-|-|-|-|-|-|-|-|-|-|')
        print(Fore.LIGHTBLACK_EX + '|-' + Fore.LIGHTCYAN_EX + 'Closer-kun ' + Fore.LIGHTYELLOW_EX + 'Version: 2.0.0' + Fore.LIGHTBLACK_EX + '-|')
        print(Fore.LIGHTBLACK_EX + '|-|-|-|-|-|-|-|-|-|-|-|-|-|-|')

    def close_processes(self):
        while True:
            running_processes = [proc for proc in psutil.process_iter() if proc.name() in self.processes]
            unique_processes = set([proc.name() for proc in running_processes])

            print(Fore.GREEN + f"+{Fore.LIGHTMAGENTA_EX} {len(unique_processes)}" + Fore.GREEN + " processes found!")
            for process in unique_processes:
                print(Fore.RED + "- " + Fore.LIGHTBLACK_EX + f"{process}")

            if running_processes:
                for proc in running_processes:
                    try:
                        proc.kill()
                    except psutil.NoSuchProcess:
                        print(Fore.RED + f"Process {proc.name()} no longer exists")
                print(Fore.RED + f"{len(unique_processes)} unique processes have been closed.")
            else:
                print(Fore.GREEN + "No processes found. Stopping.")
                break
            sleep(1)

    logging.basicConfig(filename='shutdown.log', level=logging.INFO)
    def shutdown_computer():
        response = input("Do you want to shut down the computer now? (yes/no): ")
        if response.lower() == 'yes':
            print("Shutting down the computer...")
            logging.info("Shutdown initiated.")
            if os.name == 'nt':  # Windows
                os.system('shutdown /s /t 5')
            elif os.name == 'posix':  # Unix/Linux/Mac
                os.system('shutdown -h now')
            logging.info("Shutdown command executed.")

    def execute(self):
        self.print_header()
        self.close_processes()
        self.shutdown_computer()

if __name__ == "__main__":
    closer = Closer()
    closer.execute()
