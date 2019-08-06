
class EnumMetaWithStrings(type):
    def __new__(mcs, class_name, bases, class_attrs):
        attrs = ((name, value) for name, value in class_attrs.items() if not name.startswith('__'))
        new_attrs = {'iter_items': {}}
        for name, value in attrs:
            new_attrs[name.upper()] = value[0]
            new_attrs['{}_STR'.format(name.upper())] = value[1]
            new_attrs['iter_items'][value[0]] = value[1]
        return super().__new__(mcs, class_name, bases, new_attrs)

    def __iter__(self):
        for value, value_str in self.__dict__['iter_items'].items():
            yield value, value_str
