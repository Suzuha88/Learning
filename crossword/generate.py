import sys
from itertools import permutations

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        self.domains = {
            var: set(filter(lambda v: len(v) == var.length, words))
            for var, words in self.domains.items()
        }

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False  # no revisions were made from the start
        overlap = self.crossword.overlaps[x, y]
        # don't execute if there is no overlap
        if overlap:
            # copy because original set will change size
            for wordX in self.domains[x].copy():
                # if wordX doesn't overlaps properly with all of words in y's domain then remove it
                if all([wordX[overlap[0]] != wordY[overlap[1]] for wordY in self.domains[y]]):
                    self.domains[x].remove(wordX)
                    # if revision was made, remember the fact
                    revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = list(permutations(self.domains.keys(), 2))
        else:
            queue = arcs

        while queue:
            # dequeue first arc
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) < len(self.crossword.variables):
            return False
        else:
            for value in assignment.values():
                if not value:
                    return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check unitary constraints
        for var, word in assignment.items():
            if var.length != len(word):
                return False

        # сheck binary constraints
        for var1, word1 in assignment.items():
            for var2, word2 in assignment.items():
                if var1 != var2:
                    overlap = self.crossword.overlaps[var1, var2]
                    if overlap and word1[overlap[0]] != word2[overlap[1]]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        order = dict()

        for word in self.domains[var]:
            order[word] = 0
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word == neighbor_word or word[overlap[0]] != neighbor_word[overlap[1]]:
                        order[word] += 1

        return list(reversed(sorted(order)))

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = [
            var for var in self.domains if var not in assignment]
        selected_var = None
        remaining_values = float('+inf')
        degree = 0
        for var in unassigned_variables:
            local_remaining_values = len(self.domains[var])
            # if found var with less number of values in domain
            if local_remaining_values < remaining_values:
                selected_var = var  # select this var
                remaining_values = local_remaining_values  # remember it's number of values
                # remeber it's degree
                degree = len(self.crossword.neighbors(var))

            # if there is a tie
            if local_remaining_values == remaining_values:
                local_degree = len(self.crossword.neighbors(var))
                # choose var with higher degree
                if local_degree > degree:
                    selected_var = var  # select this var
                    remaining_values = local_remaining_values  # remember it's number of values
                    # remeber it's degree
                    degree = len(self.crossword.neighbors(var))

        return selected_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment
        # select most optimal variable
        var = self.select_unassigned_variable(assignment)
        # try to assign this variable a value
        for value in self.domains[var]:
            assignment[var] = value
            # if value is consistent with csp
            if self.consistent(assignment):
                # go to next iteration of algorithm
                result = self.backtrack(assignment)
                if result:
                    return result
            # if value isn't consistent, remove it
            del assignment[var]

        # retun none if can't solve
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
