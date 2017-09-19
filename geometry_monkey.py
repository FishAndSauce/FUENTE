import numbers
import matplotlib.pyplot as plt


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

    def plt_plot_prep(self, x_range=None):
        ''' returns dict with x and y arrays for plotting StraightLine object in matplotlib.pyplot
        in the form plt.plot(plot_dict['x'], plot_dict['y'])
        '''
        if not x_range:
            if not self.x_range:
                raise ValueError('x_range must be defined for StraightLine object, else you must specify x_range parameter in plt_prep method, e.g. [2,6]')
            else:
                x_range = self.x_range
        else:
            x_range = x_range
        y_plot = [self.find_y_at_x(x_range[0]), self.find_y_at_x(x_range[1])]
        x_plot = [(x_range[0]), (x_range[1])]
        plot_dict = {'x': x_plot, 'y': y_plot}
        return plot_dict

    def quick_plot(self, *args, **kwargs):

        plot_dict = self.plt_plot_prep(x_range=self.x_range)
        plt.plot(plot_dict['x'], plot_dict['y'], *args, **kwargs)
        plt.show()

    def area_under_line(self, limits=None):

        m = self.gradient
        b = self.y_intercept

        if limits:
            x0 = limits[0]
            x1 = limits[1]
        else:
            x0 = self.x_range[0]
            x1 = self.x_range[1]

        # from calculation of definite integral of straight line
        area = m * ((x1**2) - (x0**2)) / 2 + b * (x1 - x0)
        return area


def points_to_line(points, keep_range=True):
    ''' 

    points specified as list of coords, e.g. [[1,1],[2,3]]
    '''
    x0 = points[0][0]
    y0 = points[0][1]
    x1 = points[1][0]
    y1 = points[1][1]

    m = (y1 - y0) / (x1 - x0)
    b = y1 - m * x1

    if keep_range:
        x_range = [x0, x1]

    line = StraightLine(gradient=m, y_intercept=b, x_range=x_range)
    return line
