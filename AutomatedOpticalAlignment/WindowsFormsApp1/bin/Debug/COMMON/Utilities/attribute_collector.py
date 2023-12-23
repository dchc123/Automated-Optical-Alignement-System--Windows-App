"""
| $Revision:: 278910                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-06 01:01:42 +0100 (Fri, 06 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import json
from ruamel.yaml import YAML
from COMMON.Utilities.custom_exceptions import NotSupportedError


class AttributeCollectorMixin:
    """
    Mixin utility for automatically collecting attributes and their respective values
    """

    _DEFAULT_CONFIG_FORMAT = 'json'
    _LITERALS = (bool, bytes, complex, float, int, str,)
    _ITERABLES = (list, set, tuple,)
    _MAPPINGS = (dict,)
    _ITER_POSTFIX = '__iter'
    _MAP_POSTFIX = '__map'

    def __init__(self, child_type=None, ignore_keys=None, ignore_private=True, **kwargs):
        """
        Initialize instance

        :param child_type: children type(s) used to identify them
        :type child_type: Any or tuple of Any
        :param ignore_keys: keys matching to attributes to ignore
        :type ignore_keys: str or tuple of str
        :param ignore_private: filter out private attributes
        :type ignore_private: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self._attr_child_types = child_type
        if self._attr_child_types is None:
            self._attr_child_types = AttributeCollectorMixin

        self._attr_ignore_keys = ignore_keys
        if self._attr_ignore_keys is None:
            self._attr_ignore_keys = ()

        self._attr_ignore_private = ignore_private

    def _get_attributes_list(self):
        """
        INTERNAL
        Method to generate list of all attributes

        :return: list of attributes
        :rtype: list
        """
        attr_list = []

        # filter out ignore keys, and private attributes if enabled
        for attr in vars(self).keys():
            if attr not in self._attr_ignore_keys and not (self._attr_ignore_private and attr.startswith('_')):
                attr_list.append(attr)

        return attr_list

    def _get_attributes_of_type(self, type_):
        """
        INTERNAL
        Method to retrieve a dictionary of objects of specified type(s)

        :return: dictionary of attributes and their values
        :rtype: dict
        """
        objects = {}

        # filter out ignore keys, and private attributes if enabled
        for attr, value in vars(self).items():
            if attr not in self._attr_ignore_keys \
                    and isinstance(value, type_) \
                    and not (self._attr_ignore_private and attr.startswith('_')):
                objects[attr] = value

        return objects

    def _get_configuration(self):
        """
        INTERNAL
        Method to extract state data from instance and its children

        :return: dictionary containing state information
        :rtype: dict
        """
        # retrieve list of attributes
        literals = self._get_literals()

        # Limit properties to ones that have matching setter for the eventual
        # _set_configuration() calls
        properties = self._get_properties(keys=self._get_properties_list(option='setter'))

        # retrieve child objects
        children = self._get_children()

        # retrieve iterable objects
        iterables = self._get_iterables()

        # retrieve mapping objects
        mappings = self._get_mappings()

        # build attribute dictionary for this instance
        attr_dict = {**literals, **properties}

        # check iterables for children and get their attribute dictionary
        for iter_name, iter_object in iterables.items():
            # check for none-empty iterable and get first item if not
            if len(iter_object):
                # try picking value that doesn't index at 0
                try:
                    child_obj = iter_object[0]
                    index = 0
                except IndexError:
                    child_obj = iter_object[1]
                    index = 1
            else:
                continue
            # check if iterable contains child types
            if isinstance(child_obj, self._attr_child_types):
                attr_dict_key = iter_name + AttributeCollectorMixin._ITER_POSTFIX
                attr_dict[attr_dict_key] = {}
                for child_inst in iter_object:
                    child_attr_dict = child_inst._get_configuration()
                    if child_attr_dict:
                        attr_dict[attr_dict_key][iter_name+'__'+str(index)] = child_attr_dict
                    index += 1
            # add regular iterable as is
            else:
                attr_dict[iter_name] = iter_object

        # check mappings for children and get their attribute dictionary
        for map_name, map_object in mappings.items():
            # check for none-empty mapping and get first item if not
            if len(map_object):
                child_obj = list(map_object.values())[0]
            else:
                continue
            # check if mapping contains child types
            if isinstance(child_obj, self._attr_child_types):
                attr_dict_key = map_name+AttributeCollectorMixin._MAP_POSTFIX
                attr_dict[attr_dict_key] = {}
                for child_key, child_inst in map_object.items():
                    child_attr_dict = child_inst._get_configuration()
                    if child_attr_dict:
                        attr_dict[attr_dict_key][map_name+'__'+child_key] = child_attr_dict
            # add regular mapping as is
            else:
                attr_dict[map_name] = map_object

        # get attribute dictionary for this instance's children
        for child_key, child_inst in children.items():
            child_attr_dict = child_inst._get_configuration()
            if child_attr_dict:
                attr_dict[child_key] = child_attr_dict

        return attr_dict

    def _get_children(self):
        """
        INTERNAL
        Method to retrieve a dictionary of attributes that match _child_type

        :return: dictionary of attributes and their values
        :rtype: dict
        """
        return self._get_attributes_of_type(self._attr_child_types)

    def _get_iterables(self):
        """
        INTERNAL
        Method to retrieve a dictionary of iterable attributes

        :return: dictionary of attributes and their values
        :rtype: dict
        """
        return self._get_attributes_of_type(AttributeCollectorMixin._ITERABLES)

    def _get_literals(self):
        """
        INTERNAL
        Method to retrieve a dictionary of literal attributes

        :return: dictionary of attributes and their values
        :rtype: dict
        """
        return self._get_attributes_of_type(AttributeCollectorMixin._LITERALS)

    def _get_mappings(self):
        """
        INTERNAL
        Method to retrieve a dictionary of mapping attributes

        :return: dictionary of attributes and their values
        :rtype: dict
        """
        return self._get_attributes_of_type(AttributeCollectorMixin._MAPPINGS)

    def _get_properties(self, keys):
        """
        INTERNAL
        Method to retrieve a dictionary of property attributes for the given keys

        :param keys: property keys to get values for
        :type keys: list of str
        :return: dictionary of attributes and their values
        :rtype: dict
        """
        prop_dict = {}

        for prop in keys:
            try:
                prop_dict[prop] = getattr(self, prop)
            except NotImplementedError:
                pass  # TODO [sfars] figure something for this
            except NotSupportedError:
                pass  # TODO [sfars] figure something for this

        return prop_dict

    def _get_properties_list(self, option='union'):
        """
        INTERNAL
        Method to retrieve a list of property attribute keys. It has option to limit properties
        to gettable, settable, or a combination of.

        :param option: - 'getter'
                       - 'getter_only'
                       - 'setter'
                       - 'setter_only'
                       - 'union'
                       - 'intersect'
                       - 'difference'
        :type option: str
        :return: list of property names
        :rtype: list
        """
        getter_set = set()
        setter_set = set()
        option_map = {
            'getter': 'getter_set',
            'getter_only': 'getter_set - setter_set',
            'setter': 'setter_set',
            'setter_only': 'setter_set - getter_set',
            'union': 'getter_set | setter_set',
            'intersect': 'getter_set & setter_set',
            'difference': 'getter_set ^ setter_set'
        }
        class_attr_list = []

        # filter out magic attributes, ignore keys, and private attributes if enabled
        for attr in dir(type(self)):
            if not attr.startswith('__') \
                    and attr not in self._attr_ignore_keys \
                    and not (self._attr_ignore_private and attr.startswith('_')):
                class_attr_list.append(attr)

        for attr in class_attr_list:
            attr_def = getattr(type(self), attr)
            if isinstance(attr_def, property):
                if option != 'setter' and attr_def.fget is not None:
                    getter_set.add(attr)
                if option != 'getter' and attr_def.fset is not None:
                    setter_set.add(attr)

        return list(eval(option_map[option]))

    def _set_configuration(self, attributes):
        """
        INTERNAL
        Method to apply state data to an instance and its children

        :param attributes: dictionary containing state information
        :type attributes: dict
        """
        # retrieve child objects
        children = self._get_children()

        # retrieve iterable objects
        iterables = self._get_iterables()

        # retrieve mapping objects
        mappings = self._get_mappings()

        # apply given (attribute, value) sets
        for key, value in attributes.items():
            # if an attribute is a dictionary, check if it's meant for a child instance
            if isinstance(value, dict):
                if key in children.keys():
                    children[key]._set_configuration(value)
                # Check for iterable of children
                elif key.endswith(AttributeCollectorMixin._ITER_POSTFIX):
                    for iter_key, iter_value in value.items():
                        iter_key_mod, index = iter_key.split('__')
                        index = int(index)
                        iterables[iter_key_mod][index]._set_configuration(iter_value)
                # Check for mapping of children
                elif key.endswith(AttributeCollectorMixin._MAP_POSTFIX):
                    for map_key, map_value in value.items():
                        map_key_mod, key = map_key.split('__')
                        # TODO [sfarsi] what to do if key is meant to be int?
                        mappings[map_key_mod][key]._set_configuration(map_value)
            else:
                setattr(self, key, value)

    def get(self, option="_all_"):
        """
        Single API to retrieve specific or all properties and their respective values

        :param option: specified properties to retrieve
        :type option: str or list of str
        :return: values for specified properties
        :rtype: Any or dict
        :raise AttributeError: for invalid attribute(s)
        """
        # get all literals
        literals_dict = self._get_literals()
        literals_list = list(literals_dict.keys())

        # get a list of gettable property keys
        prop_list = self._get_properties_list(option='getter')

        if option == "_all_":
            prop_dict = self._get_properties(prop_list)
            attr_dict = {**literals_dict, **prop_dict}
        else:
            option = list(option)
            # check that the requested attributes are valid
            delta = list(set(option) - set(literals_list + prop_list))
            if delta:
                raise AttributeError("Invalid attributes: {}".format(delta))

            # get literals subset
            literals_subset = list(set(literals_list) & set(option))
            literals_subset_dict = {k: literals_dict[k] for k in literals_subset}
            # get properties subset
            prop_subset = list(set(prop_list) & set(option))
            prop_subset_dict = self._get_properties(keys=prop_subset)
            # combine two dictionaries
            attr_dict = {**literals_subset_dict, **prop_subset_dict}

        return attr_dict

    def load_configuration(self, file):
        """
        Load a previously-saved state configuration from file

        :param file: file_path to state configuration
        :type file: str
        """
        if file.lower().endswith('.json'):
            format_ = 'json'
        elif file.lower().endswith('.yaml'):
            format_ = 'yaml'
        else:
            format_ = AttributeCollectorMixin._DEFAULT_CONFIG_FORMAT

        with open(file) as f:
            if format_ == 'json':
                data = json.load(f)
            else:  # 'yaml'
                yaml = YAML(typ='safe')
                data = yaml.load(f)
        f.close()
        self._set_configuration(data)

    def save_configuration(self, file):
        """
        Save current configuration to file

        :param file: file path for configuration
        :type file: str
        """
        if file.lower().endswith('.json'):
            format_ = 'json'
        elif file.lower().endswith('.yaml'):
            format_ = 'yaml'
        else:
            format_ = AttributeCollectorMixin._DEFAULT_CONFIG_FORMAT

        data = self._get_configuration()
        with open(file, 'w') as f:
            if format_ == 'json':
                json.dump(data, f, indent=4)
            else:  # 'yaml'
                yaml = YAML()
                yaml.indent = 4
                yaml.dump(data, f)
        f.close()

    def set(self, **kwargs):
        """
        Single API to configure multiple properties at once.

        **NOTE1: must use keyword arguments**

        **NOTE2: keyword argument order is retained, i.e. the attributes are applied in the
        order they are passed in**

        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        :raise TypeError: if positional arguments are used
        :raise AttributeError: for invalid attribute(s)
        """
        # get list of literals and gettable properties
        attributes = list(self._get_literals().keys()) + self._get_properties_list(option='setter')

        # check that the given attributes are valid
        delta = list(set(kwargs.keys()) - set(attributes))
        if delta:
            raise AttributeError("Invalid attributes: {}". format(delta))

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])


if __name__ == '__main__':
    class B(AttributeCollectorMixin):
        def __init__(self):
            super().__init__()
            self.attr = 1
            self._prop = 2

        @property
        def prop(self):
            return self._prop

        @prop.setter
        def prop(self, value):
            self._prop = value


    class A(AttributeCollectorMixin):
        def __init__(self):
            super().__init__()
            self.map = {'A': B(), 'B': B(), 'C': B()}
            self.iter = [B(), B(), B()]
            self.attr = 1
            self._prop = 2

        @property
        def prop(self):
            return self._prop

        @prop.setter
        def prop(self, value):
            self._prop = value

    t = A()
    t.save_configuration('AttributeCollectorMixin.json')
    t.load_configuration('AttributeCollectorMixin.json')
