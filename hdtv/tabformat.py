# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


try:
    import curses

    def get_term_width():
        # We call curses.setupterm() every time, as the terminal width
        # may have changed
        try:
            curses.setupterm()
            return curses.tigetnum("cols")
        except BaseException:
            return 80

except ImportError:
    # On platforms where we cannot load the curses library, we assume a
    # terminal width of 80 characters
    def get_term_width():
        return 80


def tabformat(cells, **kwargs):
    """
    Prints a number of cells in a layout similar to that used
    by the ``ls'' program. Expects a list of cell contents.
    Optional keyword arguments are colsepwidth, the spacing between
    two columns (defaults to 2), and tabwidth, the requested width
    of the table (defaults to width of terminal, or 80 if that
    cannot be read).
    """
    # Read keyword arguments, replace with defaults if required
    if "colsepwidth" in kwargs:
        col_sep_width = kwargs["colsepwidth"]
    else:
        col_sep_width = 2

    if "tabwidth" in kwargs:
        tabwidth = kwargs["tabwidth"]
    else:
        tabwidth = get_term_width()

    # If there are no cells, there is nothing to do...
    n_cells = len(cells)
    if n_cells == 0:
        return

    # Gather some statistics about the cells
    cell_widths = [len(cell) for cell in cells]
    min_cell_width = min(cell_widths)
    max_cell_width = max(cell_widths)

    # We use a rather simple-minded algorithm here: we know that at least one
    # column is as wide as the widest cell, while each column is at least as
    # wide as the smallest cell. This allows us to obtain an upper bound for
    # the number of columns, and thus a lower bound for the number of rows.
    # We then try to actually layout the table; if that fails, we increase the
    # decrease the number of rows and try again.
    #
    # Note that we need to try each number of rows, even if the number of
    # columns does not change, since changing the number of rows influences
    # the distribution of cells into columns, and thus the column widths.

    # Check if a two-column table *may* be possible. If not, we know that
    # we need a one-column table.
    if (max_cell_width + min_cell_width + col_sep_width) > tabwidth:
        n_cols = 1
        n_rows = n_cells
    else:
        # Calculate an upper bound for the number of columns. Note that the space
        # between two columns takes some width as well.
        n_cols = (tabwidth - max_cell_width) // (min_cell_width + col_sep_width) + 1

        # Calculate the corresponding number of rows as
        # n_rows = ceil(n_cells / n_cols), for integers
        n_rows = (n_cells - 1) // n_cols + 1

        while True:
            # Calculate the minimal number of columns for the given number of rows
            # n_cols = ceil(n_cells / n_rows), for integers
            n_cols = (n_cells - 1) // n_rows + 1

            # Try with n_cols columns, and calculate the table width.
            tbl_width = 0

            for i in range(n_cols):
                tbl_width += max(cell_widths[i * n_rows : (i + 1) * n_rows])
            # If the table is small enough, end the loop...
            if tbl_width + (n_cols - 1) * col_sep_width <= tabwidth:
                break
            # ...otherwise, increase the number of rows by one and try again
            n_rows += 1

    # Now produce the actual output
    # Calculate the individual column widths
    col_widths = []
    for i in range(n_cols):
        col_widths.append(max(cell_widths[i * n_rows : (i + 1) * n_rows]))

    # Distribute cells over rows, aloowing the table to be printed
    # row-by-row (note that successive cells go *below* each other)
    rows = [[] for i in range(n_rows)]
    for i in range(n_cells):
        rows[i % n_rows].append(cells[i])

    # Fill up rows with empty cells
    for i in range(n_rows):
        if len(rows[i]) < n_cols:
            rows[i].append("")

    # Produce the appropriate format string for output
    fmtstr = (" " * col_sep_width).join(["%%-%ds" % w for w in col_widths])

    # Output the table, row by row
    for i in range(n_rows):
        print(fmtstr % tuple(rows[i]))
