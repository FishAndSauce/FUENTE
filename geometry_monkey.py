import numbers


class StraightLine(object):
    """ A line in the form y = mx + b:

    Attributes:
        name: name of line
        gradient: value of slope of line (m)
        y_intercept: value of y at x=0 (b)
        x_range: range over which line exists as [x1, x2] (e.g. [2,6])
    """

    def __init__(self, gradient, y_intercept, x_range=None):
        self.gradient = gradient
        self.y_intercept = y_intercept
        self.x_range = x_range

        if not isinstance(gradient, numbers.Number):
            raise ValueError('gradient must be a number')
        if not isinstance(y_intercept, numbers.Number):
            raise ValueError('y_intercept must be a number')

    def find_y_at_x(self, x_value):
        """ return the value of y at a given value of x

        """
        if not isinstance(x_value, numbers.Number):
            raise ValueError('x_value argument must be a number')

        y_value = x_value * self.gradient + self.y_intercept
        return y_value

    def find_intercept_on_line(self, other_line):
        ''' finds the x value of intecept of self and another StraightLine

        '''
        if not isinstance(other_line, StraightLine):
            raise ValueError('other_line must be StraightLine objects')

        m1 = self.gradient
        m2 = other_line.gradient

        if m1 != m2:
            b1 = self.y_intercept
            b2 = other_line.y_intercept
            x = (b1 - b2) / (m2 - m1)
        else:
            x = None  # no intercept for parallel lines (m1 = m2)
        return x

    def find_intercepts_on_line(self, other_lines):
        """ takes dict of other Straightline objects to return a
        dict of their x value of intecept on self.

        other_lines in the form {"other_line_name1": x1, "other_line_name2": x2 ...etc }

        # MAKE LIST INPUT OPTION??

        """
        if not isinstance(other_lines, dict):
            raise ValueError("other_lines must be dictionary with other line's names as keys and StraightLine objects as values")

        intercepts_on_line_dict = dict()
        for other_line in other_lines:
            intercepts_on_line_dict[other_line] = self.find_intercept_on_line(
                other_lines[other_line]
            )
        return intercepts_on_line_dict
