from abc import ABC, abstractmethod
from collections import UserString
from collections.abc import (
    Mapping,
    Set,
    Sequence,
)
from decimal import Decimal
import math
from numbers import Real


def approx(item1, item2, rel_tol=1e-5, abs_tol=None):
    if abs_tol is None:
        abs_tol = 0

    handlers = [
        StringHandler(),
        RealNumHandler(),
        MappingHandler(),
        SequenceHandler(),
        SetHandler(),
        CompositeHandler(),
    ]

    for handler in handlers:
        result = handler.handle(item1, item2, rel_tol=rel_tol, abs_tol=abs_tol)
        if result is not None:
            return result

    msg = (
        'Cannot compare {item1} and {item2} '
        'of types {type1} and {type2}'
        .format(
            item1=item1, item2=item2,
            type1=type(item1), type2=type(item2),
        )
    )
    raise TypeError(msg)


class Handler(ABC):

    @abstractmethod
    def handle(self, request):
        pass


class GenericHandler(Handler):
    allowed_types = []
    forbidden_types = []

    def handle(self, item1, item2, **kwargs):
        if self.can_handle(item1, item2):
            return self.check_equal(item1, item2, **kwargs)

    def can_handle(self, item1, item2):
        return all([
            self._can_handle_one_item(item)
            for item in (item1, item2)
        ])

    def _can_handle_one_item(self, item):
        in_allowed_types = any([
            isinstance(item, type_)
            for type_ in self.allowed_types
        ])

        in_forbidden_types = any([
            isinstance(item, type_)
            for type_ in self.forbidden_types
        ])

        return in_allowed_types and not in_forbidden_types


class StringHandler(GenericHandler):
    allowed_types = [
        str,
        UserString,
    ]

    @staticmethod
    def check_equal(item1, item2, **kwargs):
        return item1 == item2


class RealNumHandler(GenericHandler):
    allowed_types = [
        Real,
        Decimal,
    ]

    def check_equal(self, item1, item2, **kwargs):
        return math.isclose(
            item1,
            item2,
            rel_tol=kwargs['rel_tol'],
            abs_tol=kwargs['abs_tol'],
        )


class MappingHandler(GenericHandler):
    allowed_types = [
        Mapping,
    ]

    @staticmethod
    def check_equal(item1, item2, **kwargs):
        if len(item1) != len(item2):
            return False

        return all(
            approx(k1, k2, **kwargs)
            and approx(v1, v2, **kwargs)
            for (k1, v1), (k2, v2)
            in zip(sorted(item1.items()), sorted(item2.items()))
        )


class SequenceHandler(GenericHandler):
    allowed_types = [
        Sequence,
    ]

    forbidden_types = [
        str,
        Mapping,
    ]

    @staticmethod
    def check_equal(item1, item2, **kwargs):
        if len(item1) != len(item2):
            return False

        return all(
            approx(val1, val2, **kwargs)
            for val1, val2
            in zip(item1, item2)
        )


class SetHandler(GenericHandler):
    allowed_types = [
        Set,
    ]

    @staticmethod
    def check_equal(item1, item2, **kwargs):
        # sets are compared exactly only
        return item1 == item2


class CompositeHandler(GenericHandler):
    def can_handle(self, item1, item2):
        return all([
            hasattr(item, '__dict__')
            for item in (item1, item2)
        ])

    @staticmethod
    def check_equal(item1, item2, **kwargs):
        return MappingHandler().handle(
            item1.__dict__,
            item2.__dict__,
            **kwargs,
        )
