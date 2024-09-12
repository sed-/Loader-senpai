import os
import time
import keyboard
import random
import shutil

class Kirby:
    requires_api = False
    requires_parameter = False
    requires_username = False

    def __init__(self):
        self.frames = [
        "<(^.^)>\n",
        "<('o')>\n",
        "<('.' )>\n",
        "<( '_' )>\n",
        "<( ._.)>\n",
        "<( '-')>\n",
        "<('-' )>\n",
        "<('_' )>\n",
        " ( '-')>\n",
        "<('-' )>\n",
        "<('-'^)\n",
        "^('-')>\n",
        "^('-')^\n",
        "<('-')>\n",
        "<( '-' )>\n",
        "<( -.-)>\n",        
        "<(^_^<)\n",
        "(>^_^)> \n",
        "<(^_^)> \n",
        "^( 'o')^ \n",
        "<('o')^ \n",
        "^('o')^ \n",
        "(^-^ )>\n",
        "<( '-'<)\n",
        "^( '-' )^\n",
        "<('.'<)\n",
        "(>'-')>\n",
        "<(^-^<)\n",
        "(>^-^)> \n",
        "<(^-^)> \n",
        "(>'_' )>\n",
        "<( '_' )>\n",
        "^( '_')^ \n",
        "(> '_' )>\n",
        "(>'.' )>\n",
        "<( '.' )>\n",
        "^( '.' )^\n",
        "(> '.' )>\n",
        "(> 'o' )>\n",
        "<( 'o' )>\n",
        "^( 'o' )^\n",
        "(> 'o' )>\n",
    ]



    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def play_animation(self):
        while not keyboard.is_pressed('s'):
            frame = random.choice(self.frames)
            self.clear_screen()
            terminal_size = shutil.get_terminal_size()
            columns, rows = terminal_size.columns, terminal_size.lines
            y = (columns - len(frame.strip())) // 2
            x = (rows // 2) - 1
            print("\n" * x + " " * y + frame.strip())
            time.sleep(0.3)
        self.clear_screen()

    def execute(self):
        self.play_animation()

# Example of the main script handling the command
if __name__ == "__main__":
    kirby = Kirby()
    kirby.execute()
