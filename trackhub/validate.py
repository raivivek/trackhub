"""
This module contains functions that are used as validators for parameters. Each
is decorated with the @validator decorator, which accepts an arbitrary number
of examples that should correctly validate.

For example, here's a validator that would be used to ensure a string has
exactly one string character:

    @validator("a", "1")
    def one_char(v):
        return isinstance(v, string_types) and len(v) == 1
"""
from textwrap import dedent
from .compatibility import string_types


class ValidationError(Exception):
    pass


def validator(*example):
    def wrapper(func):

        # Try running validation on the function's own example . . . it better
        # work!
        example_string = []
        try:
            for ex in example:
                func(ex)
                example_string.append(ex)
            example_string = 'Example value(s): %s' \
                % (" or ".join('%r' % i for i in example_string))

        except Exception as e:
            raise ValueError(
                'Error validating example (func=%s, example=%r)! '
                '\nOriginal error:\n\t%s: %s'
                % (func.__name__, example, e.__class__.__name__, e.message))

        class Validator(object):
            """
            Class to wrap a function and display an example value.
            """
            _func = func
            def __call__(self, v):
                try:
                    result = func(v)
                except Exception as e:
                    raise ValidationError(
                        '%s; %s'
                        % (e.message, example_string))
                if not result:
                    raise ValidationError(
                        '{0} failed validation using {1}; '
                        '{2}'.format(v, func.__name__, example_string))
                return result

            def __str__(self):
                return "<Validator [%s] at %s> sample: %s" \
                    % (func.__name__, id(func), example)

        return Validator()
    return wrapper


class Parameter(object):
    """
    Represents a generic parameter. Validates based on the provided possible
    values, e.g.::

        >>> Parameter("name", str).validate("asdf")
        True

        >>> Parameter("name", int).validate(999)
        True

        >>> Parameter("name", str).validate(999)
        False
    """
    def __init__(self, param, values, restrictions=None):
        self.param = param
        self.name = param
        self.values = values

    def __str__(self):
        return '<%s "%s" at %s>' \
            % (self.__class__.__name__, self.param, id(self))

    def validate(self, value):

        if isinstance(self.values, set):
            if value in self.values:
                return True

        if isinstance(self.values, type):
            if isinstance(value, self.values):
                return True
            return False

        if hasattr(self.values, '__call__'):
            result = self.values(value)
            if not result:
                raise ValidationError(
                    self.values._func.__name__, value)
            return result

        elif value == self.values:
            return True
        return False


@validator("tag=value")
def key_val(v):
    try:
        assert '=' in v
        items = v.split()
        assert len(items) == v.count('=')
        return True

    except AssertionError:
        raise ValidationError


@validator("a,b,c")
def CSV(v):
    #TODO: is a one-item list "chr1," or "chr1"?
    if isinstance(v, string_types):
        return True
    raise ValidationError


@validator("a:b:c")
def ColSV3(v):
    nvalues = 3
    if not isinstance(v, string_types):
        raise ValueError('not a string')
    vs = v.split(':')
    assert len(vs) == nvalues
    return True


@validator("a:b")
def ColSV2(v):
    nvalues = 2
    if not isinstance(v, string_types):
        raise ValueError('not a string')
    vs = v.split(':')
    assert len(vs) == nvalues
    return True


@validator("1:5", 3, "3")
def ColSV2_numbers_or_single_number(v):
    v = str(v)
    vs = v.split(':')
    assert len(vs) in [1, 2]
    for i in vs:
        try:
            float(i)
        except ValueError:
            raise ValueError(
                "{0} in parameter {1} cannot be converted "
                "into a number".format(i, v)
            )
    return True


@validator("128,0,255")
def RGB(v):
    if ' ' in v:
        raise ValueError('Space in RGB tuple')
    if "." in v:
        raise ValueError('"." in RGB tuple')
    assert isinstance(v, string_types), "RGB tuple is not a string"
    if ',' not in v:
        raise ValueError("no commas in RGB tuple")
    rgb = v.split(',')
    assert len(rgb) == 3, "RGB tuple does not have 3 values"
    try:
        rgb = map(int, rgb)
    except ValueError:
        raise ValueError('RGB tuple does not contain ints')
    for i in rgb:
        assert (0 <= i <= 255)
    return True


@validator("128,0,0 90,90,5")
def RGBList(v):
    rgbs = v.split(' ')
    assert len(rgbs) == 2, "RGBList not a space-separated list of RGB tuples"
    for i in rgbs:
        RGB(i)
    return True


@validator("off", 1)
def off_or_int(v):
    try:
        int(v)
        return True
    except ValueError:
        if v == 'off':
            return True
        raise

@validator("chr21:33031596-33033258")
def ucsc_position(v):
    try:
        chrom, pos = v.split(":")
        start, end = pos.split("-")
        start = int(start)
        end = int(end)
    except ValueError:
        raise ValueError("UCSC position string is formatted incorrectly")
    assert start >= 0, "start position must be a positive integer"
    assert end >= 0, "end position must be a positive integer"
    assert start < end, "start must be less than end"
    return True


@validator('asdf1234_33', 'AZ90')
def alphanumeric_(v):
    valid = 'abcdefghijklmnopqrstuvwxyz'
    valid += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    valid += '01234556789'
    valid += '_'
    assert isinstance(v, string_types)
    for i in v:
        if i not in valid:
            return False
    return True


@validator('one two three', 'aaaaaaaaaaaaaaaaa')
def short_label(v):
    assert isinstance(v, string_types)
    if len(v) > 17:
        raise ValueError("shortLabel is limited to 17 characters")
    return True


@validator('a' * 76, 'four five six')
def long_label(v):
    assert isinstance(v, string_types)
    if len(v)> 76:
        raise ValueError("longLable is limited to 76 characters")
    return True


@validator('https://example.com', 'path/to/a.html')
def full_or_local_url(v):
    return isinstance(v, string_types)


@validator('https://example.com', 'path/to/a.html')
def full_url(v):
    return isinstance(v, string_types)


@validator(1, '1', '500')
def int_like(v):
    try:
        int(v)
        return True
    except ValueError:
        return False


@validator(1.0, '5.556')
def float_like(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


@validator('#ff0000', 'maroon')
def hex_or_named(v):
    valid = '0123456789ABCDEF'
    try:
        if v.startswith('#'):
            assert len(v.upper()[1:]) == 6
            for i in v[1:]:
                assert i in valid
        else:
            assert v in set([
                'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple',
                'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue',
                'teal', 'aqua'])
    except AssertionError:
        return False
    return True
