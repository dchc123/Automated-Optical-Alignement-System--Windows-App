class CustomList(list):
    """
    Container for a custom iterable object for storing a list of channels.
    """
    def __init__(self, start_index=1):
        """
        Initialize instance

        :param start_index: starting index for iterable class
        :type start_index: int
        """
        super().__init__()
        self._block_index = start_index
        self._channel_list = []
        self._current = 0
        self._length = 0

        # Append None to create a list of required length
        for i in range(start_index):
            self._channel_list.append(None)

        # Default the start index for the list to 1, but allow passing a parameter to change it.
        self._start_index = start_index

    def __getitem__(self, item):
        if type(item) == int:
            if item < self._start_index:
                raise IndexError("Indexing starts at %d" % self._start_index)
            obj = self._channel_list[item]
            return obj

        elif type(item) == slice:
            if item.start is not None and item.start < self._start_index:
                raise IndexError("Indexing starts at %d" % self._start_index)
            obj = self._channel_list[item.start:
                                     item.stop:
                                     item.step]

            # Return a list without the initial 'None's that were appended above
            obj = [x for x in obj if x is not None]

            return obj
        else:
            raise TypeError

    def __iter__(self):
        self._current = 0
        return self

    def __len__(self):
        return self._length

    def __next__(self):
        if self._current == len(self._channel_list):
            raise StopIteration
        else:
            return_object = self._channel_list[self._current]

            self._current += 1

            # Recursive call the __next__ to skip when None is the current value.
            # That way, for loops will not return None
            if return_object is None:
                return_object = self.__next__()

            return return_object

    def append(self, object_):
        attr_name = 'channel_' + str(self._block_index)
        setattr(self, attr_name, object_)
        self._channel_list.append(object_)
        self._block_index += 1
        self._length += 1


class CustomDict(dict):
    """
    Container for a custom object for storing a dictionary of channels.
    """
    # TODO: add looping support to skipped named channel
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if type(key) == int:
            attr_name = 'channel_' + str(key)
            setattr(self, attr_name, value)

    def __getitem__(self, item):
        og = super().__getitem__(item)
        if type(item) == int:
            return getattr(self, 'channel_' + str(item))
        else:
            return og