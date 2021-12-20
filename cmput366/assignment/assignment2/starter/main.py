import matplotlib.pyplot as plt
import numpy as np
import time

class PlotResults:
    """
    Class to plot the results. 
    """
    def plot_results(self, data1, data2, label1, label2, filename):
        """
        This method receives two lists of data point (data1 and data2) and plots
        a scatter plot with the information. The lists store statistics about individual search 
        problems such as the number of nodes a search algorithm needs to expand to solve the problem.

        The function assumes that data1 and data2 have the same size. 

        label1 and label2 are the labels of the axes of the scatter plot. 
        
        filename is the name of the file in which the plot will be saved.
        """
        _, ax = plt.subplots()
        ax.scatter(data1, data2, s=100, c="g", alpha=0.5, cmap=plt.cm.coolwarm, zorder=10)
    
        lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
        ]
    
        ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        plt.xlabel(label1)
        plt.ylabel(label2)
        plt.grid()
        plt.savefig(filename)

class Grid:
    """
    Class to represent an assignment of values to the 81 variables defining a Sudoku puzzle. 

    Variable _cells stores a matrix with 81 entries, one for each variable in the puzzle. 
    Each entry of the matrix stores the domain of a variable. Initially, the domains of variables
    that need to have their values assigned are 123456789; the other domains are limited to the value
    initially assigned on the grid. Backtracking search and AC3 reduce the the domain of the variables 
    as they proceed with search and inference.
    """
    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
        """
        Returns a copy of the grid. 
        """
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
        """
        Returns the matrix with the domains of all variables in the puzzle.
        """
        return self._cells

    def get_width(self):
        """
        Returns the width of the grid.
        """
        return self._width

    def read_file(self, string_puzzle):
        """
        Reads a Sudoku puzzle from string and initializes the matrix _cells. 

        This is a valid input string:

        4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......

        This is translated into the following Sudoku grid:

        - - - - - - - - - - - - - 
        | 4 . . | . . . | 8 . 5 | 
        | . 3 . | . . . | . . . | 
        | . . . | 7 . . | . . . | 
        - - - - - - - - - - - - - 
        | . 2 . | . . . | . 6 . | 
        | . . . | . 8 . | 4 . . | 
        | . . . | . 1 . | . . . | 
        - - - - - - - - - - - - - 
        | . . . | 6 . 3 | . 7 . | 
        | 5 . . | 2 . . | . . . | 
        | 1 . 4 | . . . | . . . | 
        - - - - - - - - - - - - - 
        """
        i = 0
        row = []
        for p in string_puzzle:
            if p == '.':
                row.append(self._complete_domain)
            else:
                row.append(p)

            i += 1

            if i % self._width == 0:
                self._cells.append(row)
                row = []
            
    def print(self):
        """
        Prints the grid on the screen. Example:

        - - - - - - - - - - - - - 
        | 4 . . | . . . | 8 . 5 | 
        | . 3 . | . . . | . . . | 
        | . . . | 7 . . | . . . | 
        - - - - - - - - - - - - - 
        | . 2 . | . . . | . 6 . | 
        | . . . | . 8 . | 4 . . | 
        | . . . | . 1 . | . . . | 
        - - - - - - - - - - - - - 
        | . . . | 6 . 3 | . 7 . | 
        | 5 . . | 2 . . | . . . | 
        | 1 . 4 | . . . | . . . | 
        - - - - - - - - - - - - - 
        """
        for _ in range(self._width + 4):
            print('-', end=" ")
        print()

        for i in range(self._width):

            print('|', end=" ")

            for j in range(self._width):
                if len(self._cells[i][j]) == 1:
                    print(self._cells[i][j], end=" ")
                elif len(self._cells[i][j]) > 1:
                    print('.', end=" ")
                else:
                    print(';', end=" ")

                if (j + 1) % 3 == 0:
                    print('|', end=" ")
            print()

            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4):
                    print('-', end=" ")
                print()
        print()

    def print_domains(self):
        """
        Print the domain of each variable for a given grid of the puzzle.
        """
        for row in self._cells:
            print(row)

    def is_solved(self):
        """
        Returns True if the puzzle is solved and False otherwise. 
        """
        for i in range(self._width):
            for j in range(self._width):
                if len(self._cells[i][j]) != 1:
                    return False
        return True

class VarSelector:
    """
    Interface for selecting variables in a partial assignment. 

    Extend this class when implementing a new heuristic for variable selection.
    """
    def select_variable(self, grid):
        pass

class FirstAvailable(VarSelector):
    """
    Naïve method for selecting variables; simply returns the first variable encountered whose domain is larger than one.
    """
    def select_variable(self, grid):
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) > 1:
                    return (i, j)
        return None

class MRV(VarSelector):
    """
    Implements the MRV heuristic, which returns one of the variables with smallest domain. 
    """
    def select_variable(self, grid):
        remain_value = None
        variable = None
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) > 1:
                    if remain_value == None:
                        remain_value = len(grid.get_cells()[i][j])
                        variable = (i, j)
                    if remain_value != None and len(grid.get_cells()[i][j]) < remain_value:
                        remain_value = len(grid.get_cells()[i][j])
                        variable = (i, j)
        return variable


class AC3:
    """
    This class implements the methods needed to run AC3 on Sudoku. 
    """
    def remove_domain_row(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same row. 
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != column:
                new_domain = grid.get_cells()[row][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[row][j]) > 1:
                    variables_assigned.append((row, j))

                grid.get_cells()[row][j] = new_domain
        
        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same column. 
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != row:
                new_domain = grid.get_cells()[j][column].replace(grid.get_cells()[row][column], '')
                
                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[j][column]) > 1:
                    variables_assigned.append((j, column))

                grid.get_cells()[j][column] = new_domain

        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same unit. 
        """
        variables_assigned = []

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue

                new_domain = grid.get_cells()[i][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[i][j]) > 1:
                    variables_assigned.append((i, j))

                grid.get_cells()[i][j] = new_domain
        return variables_assigned, False

    def pre_process_consistency(self, grid):
        """
        This method enforces arc consistency for the initial grid of the puzzle.

        The method runs AC3 for the arcs involving the variables whose values are 
        already assigned in the initial grid. 
        """
        Q = []
        # append all the determined variable into Q
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) == 1:
                    Q.append((i, j))

        success = self.consistency(grid, Q)
        return success

    def consistency(self, grid, Q):
        """
        This is a domain-specific implementation of AC3 for Sudoku. 

        It keeps a set of variables to be processed (Q) which is provided as input to the method. 
        Since this is a domain-specific implementation, we don't need to maintain a graph and a set 
        of arcs in memory. We can store in Q the cells of the grid and, when processing a cell, we
        ensure arc consistency of all variables related to this cell by removing the value of
        cell from all variables in its column, row, and unit. 

        For example, if the method is used as a preprocessing step, then Q is initialized with 
        all cells that start with a number on the grid. This method ensures arc consistency by
        removing from the domain of all variables in the row, column, and unit the values of 
        the cells given as input. Like the general implementation of AC3, the method adds to 
        Q all variables that have their values assigned during the propagation of the contraints. 

        The method returns True if AC3 detected that the problem can't be solved with the current
        partial assignment; the method returns False otherwise. 
        """
        while Q:
            variable = Q.pop()

            # ensure consistency in row, column and unit
            variables_assigned1, result1 = self.remove_domain_row(grid, variable[0], variable[1])
            variables_assigned2, result2 = self.remove_domain_column(grid, variable[0], variable[1])
            variables_assigned3, result3 = self.remove_domain_unit(grid, variable[0], variable[1])

            if result1 == True or result2 == True or result3 == True:
                return False

            # append variables with size reduced to 1 into Q
            if variables_assigned1:
                for var in variables_assigned1:
                    Q.append(var)
            if variables_assigned2:
                for var in variables_assigned2:
                    Q.append(var)
            if variables_assigned3:
                for var in variables_assigned3:
                    Q.append(var)

        return True

class Backtracking:
    """
    Class that implements backtracking search for solving CSPs. 
    """

    def search(self, grid, var_selector):
        """
        Implements backtracking search with inference. 
        """
        # if the sudoku is solved
        if grid.is_solved():
            return grid

        # choose variable
        variable = var_selector.select_variable(grid)
        ac3 = AC3()
            
        for value in grid.get_cells()[variable[0]][variable[1]]:
            grid_copy = grid.copy()
            grid_copy.get_cells()[variable[0]][variable[1]] = value

            # check consistency
            consistent = ac3.consistency(grid_copy, [variable])
            if consistent:
                rb = self.search(grid_copy, var_selector)
                # if the subproblem returns a valid result
                if rb is not False:
                    return rb
            
            grid.get_cells()[variable[0]][variable[1]].replace(value, '')


        #----------------Code for 2.3(backtracking without AC3)-------------------
        # for value in grid.get_cells()[variable[0]][variable[1]]:
        #     consistent = True
        #     # check if value is consistent with the row
        #     for i in range(grid.get_width()):
        #         if i != variable[1] and grid.get_cells()[variable[0]][i] == value:
        #             consistent = False
        #     # check if value is consistent with the column
        #     for j in range(grid.get_width()):
        #         if j != variable[0] and grid.get_cells()[j][variable[1]] == value:
        #             consistent = False
        #     # check if value is consistent within the unit
        #     row_start = (variable[0] // 3) * 3
        #     column_start = (variable[1] // 3) * 3
        #     for i in range(row_start, row_start + 3):
        #         for j in range(column_start, column_start + 3):
        #             if i != variable[0] and j != variable[1]:
        #                 if grid.get_cells()[i][j] == value:
        #                     consistent = False
        #     # if the value is valid, choose the value and run the function again
        #     if consistent:
        #         grid_copy = grid.copy()
        #         grid_copy.get_cells()[variable[0]][variable[1]] = value
        #         rb = self.search(grid_copy, var_selector)
        #         # if the subproblem returns a valid result
        #         if rb is not False:
        #             return rb
        #         grid.get_cells()[variable[0]][variable[1]].replace(value, '')
        #--------------------------------------------------------------------------

        return False


def main():
    file = open('top95.txt', 'r')
    problems = file.readlines()

    plotter = PlotResults()
    firstavailable_time = []
    mrv_time = []

    for p in problems:
        # Read problem from string
        g = Grid()
        g.read_file(p)

        # Print the grid on the screen
        print('Puzzle')
        g.print()

        # pre-processing
        ac3 = AC3()
        success = ac3.pre_process_consistency(g)
        if not success:
            return False

        print('FirstAvailable Result:')
        # record running time of firstavailable
        firstavailable_backtracking = Backtracking()
        firstavailable_begin = time.time()
        firstavailable_backtracking.search(g, FirstAvailable()).print()
        firstavailable_end = time.time()
        firstavailable_time.append(firstavailable_end - firstavailable_begin)

        print('MRV Result:')
        # record running time of mrv
        mrv_backtracking = Backtracking()
        mrv_begin = time.time()
        mrv_backtracking.search(g, MRV()).print()
        mrv_end = time.time()
        mrv_time.append(mrv_end - mrv_begin)

    # plot plots
    plotter.plot_results(mrv_time, firstavailable_time, "Running Time Backtracking (MRV)", "Running Time Backtracking (FA)", "running_time")

    return True


if __name__ == "__main__":
    main()