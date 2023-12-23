import COMMON  # Required to resolve relative paths
import os.path


def resolve_file_path(filename):
    """
    Resolve a filename and determine whether it is specified as an absolute path,
    relative path or a relative path to the main top level CLI directory.

    :param filename: original filename
    :type filename: str
    :return: the resolved filename which can be used in open() calls
    :rtype: str
    """
    common_path = COMMON.__path__[0]

    full_path_common = common_path + "\\" + filename

    if os.path.isfile(full_path_common):
        return os.path.abspath(full_path_common)
    elif os.path.isfile(filename):
        return os.path.abspath(filename)
    else:
        raise OSError("File %s was not found" % filename)
