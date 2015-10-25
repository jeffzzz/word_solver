import argparse
import logging


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
        self.valid_letters = None
        try:
            with open(fname) as f:
                self.puzzle_len = int(f.readline())
                if runmode == 'letter':
                    self.valid_letters = [[] for _ in range(self.puzzle_len)]
                for line in f:
                    category = line.split(':')[0]
                    category_path = './wordlist/{0}.txt'.format(category)
                    words = []
                    with open(category_path) as f0:
                        for word in f0:
                            words.append(word.rstrip('\r\n'))

                    indices = [int(x) - 1 for x in line.split(':')[1].split(', ')]
                    self.categories[category] = (indices, words)
                    if runmode == 'letter':
                        self.valid_letters[indices[0]].append((category, list(set([x[0] for x in words]))))
                        self.valid_letters[indices[1]].append((category, list(set([x[1] for x in words]))))
                        self.valid_letters[indices[2]].append((category, list(set([x[2] for x in words]))))
        except OSError:
            logger.error('Could not open puzzle.')

    def __is_solution(self, res):
        """ Check if result is a solution the puzzle"""
        if len(res) == self.puzzle_len:
            for category, (idxs, words) in self.categories.items():
                word = res[idxs[0]] + res[idxs[1]] + res[idxs[2]]
                if word in words:
                    return False
            return True
        else:
            return False

    def __is_valid(self, res):
        """ Check if result is valid so far (consistency check) """
        pass

    def _solve_letter(self, res=list(), index=0):
        pass

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