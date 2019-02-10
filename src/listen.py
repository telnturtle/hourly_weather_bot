import google_weather
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# import nalssi


title = 'Nalssi tester'

cmd_text = 'Type location, help or exit'
line_text = 'location | help | exit > '
help_text = 'Type "exit" for exit'
cannot_text = 'Cannot found'

exit_cmd = 'exit'
help_cmd = 'help'


print(title)
print(cmd_text)
print()

while True:
    s = input(line_text)
    if s == exit_cmd:
        break
    elif s == help_cmd:
        print(help_text)
    elif s == '':
        print(cmd_text)
    else:
        try:
            # print(nalssi.condition_hourly(s))
            print(google_weather.weather(s))
        except Exception as e:
            print(cannot_text)
    print()
