import argparse
import copy
import heapq
import logging

from collections import Counter
from operator import itemgetter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LetterCounter:

    def __init__(self, letters):
        self.letters = letters
        for letter in self.letters:
            self.letters[letter] = [self.letters[letter], 'unmarked']

    def __repr__(self):
        return str(self.letters)

    def __len__(self):
        return len(self.letters.keys())

    def get_mark(self, letter):
        return self.letters[letter][1]

    def mark(self, letter):
        self.letters[letter][1] = 'marked'

    def unmark(self, letter):
        self.letters[letter][1] = 'unmarked'

    def most_common(self, n=None):
        print(self.letters.items())
        if n is None:
            return sorted(self.letters.items(), key=lambda x: x[1][0] if x[1][1] != 'marked' else 0, reverse=True)
        return heapq.nlargest(n, self.letters.items(), key=lambda x: x[1][0] if x[1][1] != 'marked' else 0)

    def clear_counts(self):
        for letter in self.letters:
            self.letters[letter][0] = 0

    def add(self, letter, count=None):
        if letter in self.letters:
            if count:
                self.letters[letter][0] = count
            else:
                self.letters[letter][0] += 1
        else:
            self.letters[letter] = [0, 'unmarked']

    def purge(self):
        self.letters = {letter:data for letter, data in self.letters.items() if data[0] > 0}


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
                    self.valid_categories[indices[0]].append(category)
                    self.valid_categories[indices[1]].append(category)
                    self.valid_categories[indices[2]].append(category)
                    if runmode == 'letter':
                        self.valid_letters[indices[0]].append([x[0] for x in words])
                        self.valid_letters[indices[1]].append([x[1] for x in words])
                        self.valid_letters[indices[2]].append([x[2] for x in words])
        except OSError:
            logger.error('Could not open puzzle.')

        for i, category in enumerate(self.valid_letters):
            for j in range(len(category)):
                category[j] = Counter(category[j])
                if j == 0:
                    intersection = category[j].keys()
                else:
                    intersection &= category[j].keys()
            for j in range(len(category)):
                invalid_keys = category[j].keys() - intersection
                for key in invalid_keys:
                    del category[j][key]
            self.valid_letters[i] = [self.valid_letters[i][0], 'unvisited']
        for i, category in enumerate(self.valid_letters):
            self.valid_letters[i][0] = LetterCounter(dict(self.valid_letters[i][0]))

    def __is_solution(self, res):
        """ Check if result is a solution the puzzle """
        for category, (indices, words) in self.categories.items():
            word = res[indices[0]] + res[indices[1]] + res[indices[2]]
            if word not in words:
                return False
        return True

    def __get_valid_letters(self, index, letters, letter):
        """
        Get new list of valid letters, removing words that don't have letter in the correct position.

        Args:
            index (int): Index of the current char to assigned.
            letters (list): List of counters that keep track of valid letters for every index.
            letter (char): Character that was just assigned.

        Returns:
            list: New list of counters for valid letters at each index
        """
        categories = self.valid_categories[index]
        new_valid_letters = [None] * self.puzzle_len
        for category in categories:
            indices, words = self.categories[category]
            indices = [x if x != index else None for x in indices]
            pos = indices.index(None)
            words = [x for x in words if x[pos] == letter]
            for i, idx in enumerate(indices):
                if idx is not None:
                    new_valid_letters[idx] = Counter([x[i] for x in words])

        for i, counter in enumerate(letters):
            if new_valid_letters[i]:
                counter[0].clear_counts()
        for i, counter in enumerate(new_valid_letters):
            if counter:
                for letter, count in counter.items():
                    letters[i][0].add(letter, count)
        for counter, _ in letters:
            counter.purge()

        return letters

    def _solve_letter(self, index, valid_letters, res=None, marked=None):
        """
        Solves the puzzle using backtracking with letter by letter assignment.

        Args:
            index (int): List of indexes passed in
            valid_letters (list): List of counters that keep track of valid letters for every index.
            res (list): Current result. Defaults to None.
        """
        if not res:
            res = [None] * self.puzzle_len
        if len([x for x in res if x]) == self.puzzle_len:
            if self.__is_solution(res):
                logger.info('Solution found!')
                print(res)
                return True
            else:
                return False
        letter, mark = valid_letters[index][0].most_common()[0]
        if mark == 'marked':
            return
        res[index] = letter
        valid_letters[index][0].mark(letter)
        valid_letters[index][1] = 'visited'
        valid_letters = self.__get_valid_letters(index, valid_letters, letter)
        next_index = valid_letters.index(min(valid_letters, key=lambda x:
                                        len(x[0]) if x and x[1] != 'visited' else float('inf')))
        return self._solve_letter(next_index, valid_letters, res)

    def _solve_word(self):
        pass

    def solve(self):
        if self.runmode == 'letter':
            index = self.valid_letters.index(min(self.valid_letters, key=lambda x: len(x[0])))
            valid_letters = copy.deepcopy(self.valid_letters)
            self._solve_letter(index, valid_letters)
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