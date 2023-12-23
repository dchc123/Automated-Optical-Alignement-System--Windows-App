"""
Current COMMON version as 'major.minor.micro' and can be sub queried as.

"""
from git import Repo


class _COMMONVersion:
    """
    Simple version class to enable sub version access without sting parsing
    """
    def __init__(self, major, minor, micro):
        self.major = major
        self.minor = minor
        self.micro = micro

    @property
    def value(self):
        """
        **READONLY**

        :value: full version in #.#.# format
        :type: str
        """
        return "{}.{}.{}".format(self.major, self.minor, self.micro)


r = Repo('.', search_parent_directories=True)
v = r.git.describe('--tags').split('.')

version = _COMMONVersion(*v)
__version__ = version.value
