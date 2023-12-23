import sys
import fileinput


file_path = sys.argv[1]

with fileinput.FileInput(file_path, inplace=True) as file:
    for line in file:
        print(line.replace('#c.Completer.greedy = False', 'c.Completer.greedy = True'), end='')

with fileinput.FileInput(file_path, inplace=True) as file:
    for line in file:
        print(line.replace('#c.Application.log_level = 30', 'c.Application.log_level = 20'), end='')  # INFO=20




