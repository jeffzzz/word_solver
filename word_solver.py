import argparse
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordSolver:

    def __init__(self, fname, runmode):
        self.runmode = runmode
        self.puzzle_soln = []
        self.indices = {}
        self.words = {}

        with open(fname) as f:
            puzzle_len = int(f.readline())
            self.puzzle_soln = [''] * puzzle_len
            for line in f:
                category = line.split(':')[0]
                indices = [int(x) - 1 for x in line.split(':')[1].split(', ')]
                self.indices[category] = indices

        for category in self.indices:
            self.words[category] = []
            category_path = './wordlist/{0}.txt'.format(category)
            with open(category_path) as f:
                for line in f:
                    self.words[category].append(line.rstrip('\r\n'))



def main():
    parser = argparse.ArgumentParser(description='''Word solver for CS 440 by
                                                    Shibo Yao, Mike Chen,
                                                    and Jeff Zhu''')
    parser.add_argument('fname', help='Input word puzzle')
    parser.add_argument('runmode', help='''Choose a backtracking search
                                        assignment algorithm: letter, word''')
    args = parser.parse_args()

    ws = WordSolver(args.fname, args.runmode)


if __name__ == '__main__':
    main()