import google_weather
import google_aq
import print_exception
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
            # # A
            # print(nalssi.condition_hourly(s))
            # B
            # print(google_weather.weather(s))
            # print(google_aq.aq(s))
            # C
            print(google_weather.hourly_daily(s))
        except Exception as e:
            print_exception.print_()
            print(cannot_text)
    print()
