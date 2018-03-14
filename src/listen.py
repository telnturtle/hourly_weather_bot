import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import nalssi
import transloc


print("Nalssi tester")


while True:
    s = input('NG > ')
    if s == 'quit':
        break
    elif s == 'help':
        print('Type "quit" for quit')
    else:
        print(nalssi.condition_hourly(s))
