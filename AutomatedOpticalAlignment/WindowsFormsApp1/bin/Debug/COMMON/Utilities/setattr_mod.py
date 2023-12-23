"""
| $Revision:: 282944                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-18 21:49:13 +0100 (Thu, 18 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import inspect


class BlockSetattrMixin:
    """
    Mixin utility to block accidentally assigning/overriding method and specific objects
    """
    _global_active = False

    def __init__(self, object_type, **kwargs):
        """
        Initialize instance

        :param object_type: object type(s) to prevent re-assignment of
        :type object_type: Any of tuple of Any
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self._setattr_block_types = object_type

    def __setattr__(self, key, value):
        """
        MAGIC
        Overwriting setattr to catch accidental overwriting of methods and specific objects

        :param key: name of attribute
        :type key: str
        :param value: new value for attribute
        :type value: Any
        """
        # TODO [sfarsi] slight hack to get around the global nature of this mixin. If a driver is created
        # after another is already connected, the new driver may hit this block if anything in its init.
        # The proper fix would be to have one lock per driver instance and its sub-blocks.
        stack = inspect.stack()

        if BlockSetattrMixin._global_active \
                and not (hasattr(type(self), key) and isinstance(getattr(type(self), key), property)) \
                and hasattr(self, key) and stack[1][3] != "__init__":
            attr_value = getattr(self, key)
            if isinstance(attr_value, self._setattr_block_types):
                raise AttributeError("Attempted to overwrite object assigned to '{}'. Use '_block_setattr()' and"
                                     "'_unblock_setattr()' calls for intentional modifications.".format(key))
            if callable(getattr(self, key)):
                raise AttributeError("Attempted to overwrite method '{}'. Use '_block_setattr()' and "
                                     "'_unblock_setattr()' calls for intentional modifications.".format(key))
        object.__setattr__(self, key, value)

    def _block_setattr(self):
        """
        INTERNAL
        Method to freeze setattr for methods and specific objects
        """
        BlockSetattrMixin._global_active = True

    def _unblock_setattr(self):
        """
        INTERNAL
        Method to unfreeze setattr for methods and specific objects
        """
        BlockSetattrMixin._global_active = False


if __name__ == '__main__':
    class A(BlockSetattrMixin):
        cls_var = 4

        def __init__(self):
            super().__init__(BlockSetattrMixin)
            self.obj = BlockSetattrMixin(str)

        @property
        def prop(self):
            return

        @prop.setter
        def prop(self, value):
            pass

        def method(self):
            pass

    t = A()
    t._block_setattr()
    t.cls_var = 3
    t.prop = 4
    try:
        t.obj = object()
    except AttributeError:
        print('Caught object re-assignment')
    try:
        t.method = 'foo'
    except AttributeError:
        print('Caught method overriding')
