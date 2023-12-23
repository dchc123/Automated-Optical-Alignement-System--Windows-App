"""
| $Revision:: 278787                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-03 01:43:55 +0100 (Tue, 03 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import importlib
import os


def collect(path, cls, user_prompt=False, skip_base=True):
    """
    Method that returns a list of class definitions in a package
    :param path: package path
    :param cls: base class
    :param user_prompt: option to display prompts to select classes
    :param skip_base: option to skip base definitions
    :return: list
    """
    paths = []
    for path, subdirs, files in os.walk(path):
        for name in subdirs:
            if '__' not in name:
                paths.append(os.path.join(path, name).replace('\\', '.'))

    for path in paths:
        importlib.import_module(path)

    class_definitions = get_subclasses(cls, skip_base)

    if user_prompt:
        ret = prompt(class_definitions)
    else:
        ret = class_definitions

    return ret


def get_subclasses(cls, skip_base):
    """
    Recursive call to return all sub classes of a base class
    :param cls: base class
    :param skip_base: option to skip base definitions
    :return: list
    """
    class_definitions = [x for x in cls.__subclasses__() if 'Base' not in x.__name__ or not skip_base]

    for s in cls.__subclasses__():
        class_definitions += get_subclasses(s, skip_base)
    return class_definitions


def prompt(object_list):
    """
    Prompts the user given prompt lists and returns objects accordingly
    :param object_list: objects to be returned
    :return: list
    """
    prompt_list = [x.__base__.__name__.replace('Base', '')
                   + ' '
                   + '-'*(20 - len(x.__base__.__name__.replace('Base', '')))
                   + ' '
                   + x.__name__ for x in object_list]

    for index, prompt_name in enumerate(prompt_list):
            print(index, (5-len(str(index)))*"-", prompt_name, )

    chosen_objects = list(input('Classes:').strip().split(','))

    return_list = []
    for index in chosen_objects:
        return_list.append(object_list[int(index)])

    return return_list
