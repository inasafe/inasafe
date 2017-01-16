# coding=utf-8
"""Module to generate context for SVG Chart.
This context then used for SVG Jinja2 generation.
"""
import math

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class SVGChartContext(object):

    """Context to hold information to generate SVG."""

    def __init__(self, as_file=False):
        """Hold context for SVG generation.

        :param as_file: Information to generate the svg as file
        :type as_file: bool
        """
        self._as_file = as_file

    @property
    def as_file(self):
        """Tell generator that this svg will be generated as a file.

        :return: boolean value
        :rtype: bool
        """
        return self._as_file

    @as_file.setter
    def as_file(self, value):
        """Setter for as_file property

        :param value: boolean value
        :type value: bool
        """
        self._as_file = value

    @classmethod
    def _convert_tuple_color_to_hex(cls, color):
        """Convert tuple of color element (r, g, b) to hexa.

        :param color: A color tuple
        :type color: (int, int, int) | str

        :return: Hexa representation of the color
        :rtype: str
        """
        if isinstance(color, tuple):
            return '#{:02x}{:02x}{:02x}'.format(*color)
        elif isinstance(color, str):
            if not color.startswith('#'):
                return '#{color_hex}'.format(color_hex=color)
            else:
                return color
        else:
            return '#000'


class DonutChartContext(SVGChartContext):

    """Context to hold information to generate donut chart."""

    DEFAULT_RADIUS = 128

    def __init__(
            self,
            data=None,
            labels=None,
            colors=None,
            inner_radius_ratio=None,
            title=None,
            total_header=None,
            thousand_separator_format='{0:,}',
            stroke_color=None,
            as_file=False):
        """Hold context for donut chart generation.

        :param data: a list of values to show as donut chart
        :type data: list[float]

        :param labels: a list of labels to associated with the data
        :type labels: list[str]

        :param colors: a list of colors (rgb value tuple, hex string)
            associated with the data
        :type colors: list[(int, int, int)] | list[str]

        :param as_file: Information to generate the svg as file
        :type as_file: bool

        :param inner_radius_ratio: ratio of hollowness of the pie chart
            to make a donut
        :type inner_radius_ratio: float

        :param title: the title of the chart
        :type title: str

        :param stroke_color: color of the outer strok of each slice
        :type stroke_color: str | (int, int, int)

        :param total_header: the name of the total value that will be written
            inside the donut
        :type total_header: str

        :param thousand_separator_format: thousand separator format of
            python 3 style
        :type thousand_separator_format: str

        :param
        """
        super(DonutChartContext, self).__init__(as_file=as_file)
        self._data = data
        self._inner_radius_ratio = inner_radius_ratio
        if not stroke_color:
            stroke_color = '#fff'
        self._stroke_color = self._convert_tuple_color_to_hex(stroke_color)
        self._title = title
        self._total_header = total_header
        self._thousand_separator_format = thousand_separator_format
        if data:
            data_length = len(data)
            if not labels:
                labels = ['' for i in range(data_length)]

            if not colors:
                # create blue spectrum
                colors = [
                    (255, 255, i * 256 / data_length) for i
                    in range(data_length)]
            else:
                self._colors = []
                for c in colors:
                    self._colors.append(
                        self._convert_tuple_color_to_hex(c))

            self._labels = labels
            self._colors = colors

    @property
    def inner_radius_ratio(self):
        """Ratio of how big the inner radius is.
        Used to create donut chart

        :return: Ratio value [0,1]
        :rtype: float
        """
        return self._inner_radius_ratio

    @property
    def stroke_color(self):
        """Stroke color when drawing slices.
        Color represented as hex string

        :return: Color hex
        :rtype: str
        """
        return self._stroke_color

    @property
    def title(self):
        """Title of the chart.

        :return: title
        :rtype: str
        """
        return self._title

    @property
    def total_header(self):
        """The header for total description.

        :return: title header
        :rtype: str
        """
        return self._total_header

    @property
    def thousand_separator_format(self):
        """Thousand separator format in Python 3 style.
        Default value is '{0:,}'

        :return: python string format
        :rtype: str
        """
        return self._thousand_separator_format

    @property
    def data(self):
        """Data array contains values.

        :return: list of values
        :rtype: list[float]
        """
        return self._data

    @property
    def labels(self):
        """Label arrays contains strings.

        :return: list of string
        :rtype: list[str]
        """
        return self._labels

    @property
    def colors(self):
        """List of colors represented as hex strings.

        :return: list of string
        :rtype: list[str]
        """
        return self._colors

    @property
    def total_value(self):
        """Total sum of data array.

        :return: total
        :rtype: float
        """
        return sum(self.data)

    @property
    def data_object(self):
        """List of dictionary contains value and labels associations.

        :return: list of dictionary
        :rtype: list[dict]
        """
        data_obj = []

        for i in range(0, len(self.data)):
            obj = {
                'value': self.data[i],
                'label': self.labels[i],
                'color': self.colors[i],
            }
            data_obj.append(obj)
        return data_obj

    @property
    def slices(self):
        """List of dictionary context to generate pie slices in svg.

        :return: list of dictionary
        :rtype: list[dict]
        """
        labels = self.labels
        values = self.data
        hole_percentage = self.inner_radius_ratio
        radius = self.DEFAULT_RADIUS
        hole = hole_percentage * radius
        colors = self.colors
        stroke_color = self.stroke_color

        slices_return = []
        total_values = self.total_value
        angle = - math.pi / 2
        center_point = (128, 128)
        label_position = None
        for idx, v in enumerate(values):
            step_angle = 1.0 * v / total_values * 2 * math.pi
            # move marker
            d = ''
            d += 'M%f,%f' % (
                radius * math.cos(angle) + center_point[0],
                radius * math.sin(angle) + center_point[1])
            # outer arc, counterclockwise
            next_angle = angle + step_angle
            d += 'a%f,%f 0 0 1 %f,%f' % (
                radius, radius,
                radius * (math.cos(next_angle) - math.cos(angle)),
                radius * (math.sin(next_angle) - math.sin(angle))
            )
            # if hole == 0 then only pie chart
            if not hole == 0:
                # line in
                inner_radius = radius - hole
                d += 'l%f,%f' % (
                    - inner_radius * math.cos(next_angle),
                    - inner_radius * math.sin(next_angle)
                )

                # inner arc
                d += 'a%f,%f 0 0 0 %f,%f' % (
                    hole, hole,
                    hole * (math.cos(angle) - math.cos(next_angle)),
                    hole * (math.sin(angle) - math.sin(next_angle))
                )

            # close path
            d += 'Z'

            # calculate center of slice to put value text
            mean_angle = angle + step_angle / 2
            center_slice_radius = radius / 2
            if not hole == 0:
                # skew radius outwards, because inner circle is hollow
                center_slice_radius += inner_radius / 2
            # calculate center of slice, angle increments clockwise
            # from 90 degree position
            center_slice_x = (
                center_point[0] +
                center_slice_radius * math.cos(mean_angle))
            center_slice_y = (
                center_point[1] +
                center_slice_radius * math.sin(mean_angle))

            # calculate where to put labels for slice
            # decide which side to show
            if not label_position:
                label_position_x = 2 * center_point[0]
                label_position_y = 0
            # if - math.pi / 2 < mean_angle < math.pi / 2:
            #     # put it on the right side
            #     label_position_y += 20
            label_position_y += 20
            label_position = (label_position_x, label_position_y)

            angle = next_angle
            one_slice = {
                'center': (center_slice_x, center_slice_y),
                'path': d,
                'fill': colors[idx],
                'label_position': label_position,
                'value': v,
                'percentage': v * 100.0 / total_values,
                'label': labels[idx],
                'stroke': stroke_color,
                'stroke_opacity': 1
            }

            slices_return.append(one_slice)

        return slices_return
