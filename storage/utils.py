class ChoiceBase(object):
        """The base which allows classes to define string attributes choices.

          A child class can definite attributes having string values which will be
          collected using the Choices() classmethod. Helps emulate a simple string enum
          style class. The child classes can be used to extend and form a superset
          choice class.

          Example:

            class Move1D(ChoiceBase):
              LEFT='go_left'
              RIGHT='go_right'

            class Move2D(Move1D)
              FOWARD='go_forward'
              BACKWARD='go_backward'

            Move1D.Choices() == ['go_left', 'go_right']
            Move2D.Choices() == ['go_left', 'go_right', 'go_forward', 'go_backward']
          """

        @classmethod
        def Choices(cls):
                """Determines all the string valued enum choices present in a class.

                    Returns:
                        A set of acceptable string value choices.
                    """
                attr = '_choice_attr_' + cls.__name__
                if hasattr(cls, attr):
                        return getattr(cls, attr)

                choices = set()
                for (k, v) in cls.__dict__.items():
                        if not k.startswith('_') and issubclass(type(v), (str, unicode)):
                                choices.add(v)
                for base in cls.__bases__:
                        if issubclass(base, ChoiceBase) and base is not ChoiceBase:
                                choices = set.union(choices, base.Choices())
                setattr(cls, attr, choices)

                return choices
