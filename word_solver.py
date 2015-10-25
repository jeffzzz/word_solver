import argparse
import logging

from collections import Counter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordSolver:

    def __init__(self, fname, runmode):
        if runmode.lower() != 'letter' and runmode.lower() != 'word':
            logger.error('Invalid runmode.')
            raise SystemExit
        self.runmode = runmode.lower()
        self.puzzle_solutions = []
        self.puzzle_len = 0
        self.categories = {}
        self.valid_categories = None
        self.valid_letters = None
        try:
            with open(fname) as f:
                self.puzzle_len = int(f.readline())
                self.valid_categories = [[] for _ in range(self.puzzle_len)]
                if runmode == 'letter':
                    self.valid_letters = [{} for _ in range(self.puzzle_len)]

                for line in f:
                    category = line.split(':')[0]
                    category_path = './wordlist/{0}.txt'.format(category)
                    words = []
                    with open(category_path) as f0:
                        for word in f0:
                            words.append(word.rstrip('\r\n'))

                    indices = [int(x) - 1 for x in line.split(':')[1].split(', ')]
                    self.categories[category] = (indices, words)
                    self.valid_categories[indices[0]].append(category)
                    self.valid_categories[indices[1]].append(category)
                    self.valid_categories[indices[2]].append(category)
                    if runmode == 'letter':
                        for word in words:
                            self.valid_letters[indices[0]].append([x[0] for x in words])
                            self.valid_letters[indices[1]].append([x[1] for x in words])
                            self.valid_letters[indices[2]].append([x[2] for x in words])
        except OSError:
            logger.error('Could not open puzzle.')

    def __is_solution(self, res):
        """ Check if result is a solution the puzzle"""
        for category, (idxs, words) in self.categories.items():
            word = res[idxs[0]] + res[idxs[1]] + res[idxs[2]]
            if word in words:
                return False
        return True

    def _solve_letter(self, res=list(), index=None):
        if len(res) == self.puzzle_len:
            if self.__is_solution(res):
                self.puzzle_solutions.append(res)
            return

    def _solve_word(self):
        pass

    def solve(self):
        if self.runmode == 'letter':
            self._solve_letter()
        elif self.runmode == 'word':
            self._solve_word()


def main():
    parser = argparse.ArgumentParser(description='''Word solver for CS 440 by
                                                    Shibo Yao, Mike Chen,
                                                    and Jeff Zhu''')
    parser.add_argument('fname', help='Input word puzzle')
    parser.add_argument('runmode', help='''Choose a backtracking search
                                        assignment algorithm: letter, word''')
    args = parser.parse_args()

    ws = WordSolver(args.fname, args.runmode)
    ws.solve()


if __name__ == '__main__':
    main()