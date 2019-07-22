
class EnumMetaWithStrings(type):
    def __new__(mcs, class_name, bases, class_attrs):
        attrs = ((name, value) for name, value in class_attrs.items() if not name.startswith('__'))
        new_attrs = {}
        for name, value in attrs:
            new_attrs[name.upper()] = value[0]
            new_attrs['{}_STR'.format(name.upper())] = value[1]
        return super().__new__(mcs, class_name, bases, new_attrs)
