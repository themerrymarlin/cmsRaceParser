import sys
import os
import time
import race_parser


# monitors a directory for new files and calls the results parser if they're json
def main(argv):
    path_to_watch = argv[0]
    before = dict([(f, None) for f in os.listdir(path_to_watch)])
    while 1:
        time.sleep(60)
        after = dict([(f, None) for f in os.listdir(path_to_watch)])
        added = [f for f in after if f not in before]
        if added:
            for new_file in added:
                if new_file.endswith('.json'):
                    race_parser.main(new_file)
        before = after


if __name__ == '__main__':
    main(sys.argv[1:])
