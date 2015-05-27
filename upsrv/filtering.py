#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import datetime
import dateutil.parser
import dateutil.tz
import re
import sys

import logging
log = logging.getLogger(__name__)

_tzutc = dateutil.tz.tzutc()
def parseDate(value):
    return dateutil.parser.parse(value, default=datetime.datetime.now().replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0,
        tzinfo=_tzutc))

class InvalidData(Exception):
    def __init__(self, *args, **kwargs):
        msg = kwargs.pop('msg', None)
        super(InvalidData, self).__init__(*args, **kwargs)
        self.msg = msg

class Operator(object):
    filterTerm = None
    operator = None
    description = None
    arity = 2
    # Variable length arguments
    ARITY_VAROP = object()
    ARITY_VAR = object()
    # This may look weird, but we need two backslashes when trying to
    # match a single one, for escaping reasons
    _singleBackslashRe = re.compile(r'\\')

    def __init__(self, *operands):
        self.operands = list(operands)

    def addOperand(self, operand):
        self.operands.append(operand)

    def asString(self):
        return "%s(%s)" % (self.filterTerm,
            ','.join((hasattr(x, 'asString') and x.asString() or self._quote(x))
                for x in self.operands))

    @classmethod
    def _quote(cls, s):
        s = cls._singleBackslashRe.sub(r'\\\\', s)
        slen = len(s)
        s = s.replace('"', r'\"')
        if len(s) != slen:
            # We've replaced something
            s = '"%s"' % s
        return s

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not isinstance(self, other.__class__):
            return False
        if len(self.operands) != len(other.operands):
            return False
        for ssub, osub in zip(self.operands, other.operands):
            if ssub != osub:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def castValue(self, value):
        return value

    def expression(self, model):
        field = None
        if self.arity == 2:
            (field, value) = self.operands
        elif self.arity is self.ARITY_VAROP:
            (field, value) = self.operands[0], self.operands[1:]
        elif self.arity is self.ARITY_VAR:
            if not self.operands:
                raise Exception("Operator expected at least one argument")
            exprs = [ x.expression(model) for x in self.operands ]
            value = None
            for v in exprs:
                if value is None:
                    value = v
                else:
                    value = getattr(value, self.operator)(v)
            return value
        else:
            raise Exception("Unsupported arity %s" % self.arity)
        column = model.__table__.columns.get(field, None)
        if column is None:
            raise InvalidData(msg="Invalid column %s" % field)
        columnInstr = getattr(model, field)
        if column.type.__class__.__name__ == 'DateTime':
            try:
                value = parseDate(value)
            except (TypeError, ValueError), e:
                raise InvalidData(msg="Invalid time specification '%s'" %
                    value)
        func = getattr(columnInstr, self.operator)
        return func(value)

class BooleanOperator(Operator):
    def castValue(self, value):
        if value.lower() == 'false':
            return False
        return True

class InOperator(Operator):
    filterTerm = 'IN'
    operator = 'in_'
    description = 'In list'
    arity = Operator.ARITY_VAROP

class NotInOperator(InOperator):
    filterTerm = 'notin_'
    description = 'Not in list'

class NullOperator(BooleanOperator):
    filterTerm = 'IS_NULL'
    operator = 'is_'
    description = 'Is NULL'

class EqualOperator(Operator):
    filterTerm = 'EQ'
    operator = '__eq__'
    description = 'Equal to'

class NotEqualOperator(EqualOperator):
    filterTerm = 'NE'
    operator = '__ne__'
    description = 'Not equal to'

class LessThanOperator(Operator):
    filterTerm = 'LT'
    operator = '__lt__'
    description = 'Less than'

class LessThanEqualOperator(Operator):
    filterTerm = 'LE'
    operator = '__le__'
    description = 'Less than or equal to'

class GreaterThanOperator(Operator):
    filterTerm = 'GT'
    operator = '__gt__'
    description = 'Greater than'

class GreaterThanEqualOperator(Operator):
    filterTerm = 'GE'
    operator = '__ge__'
    description = 'Greater than or equal to'

class LikeOperator(Operator):
    filterTerm = 'LIKE'
    operator = 'like'
    description = 'Like'

class NotLikeOperator(LikeOperator):
    filterTerm = 'NOT_LIKE'
    operator = 'notlike'
    description = 'Not like'

class ContainsOperator(Operator):
    filterTerm = 'CONTAINS'
    operator = None
    description = "Contains"
    arity = Operator.ARITY_VAROP

class AndOperator(Operator):
    filterTerm = 'AND'
    operator = '__and__'
    description = "And"
    arity = Operator.ARITY_VAR

class OrOperator(Operator):
    filterTerm = 'OR'
    operator = '__or__'
    description = "Or"
    arity = Operator.ARITY_VAR

def operatorFactory(operator):
    return operatorMap[operator]

class Lexer(object):
    """
    Class used for parsing a query tree.
    The general syntax is, in BNF-like syntax:

    optree ::== OPERATOR(operand[,operand*])
    OPERATOR ::== (word)
    operand ::== string | quotedstring | optree
    string ::== (pretty obvious)
    quotedstring :== " | string | "

    Strings MUST be quoted if they contain a quote (which must be escaped with
    a backslash), paranthesis or commas. Simple words do not have to be quoted,
    as they do not break the parser. Backslashes have to be doubled up within
    quotes.

    Example of operands that evaluate to strings::
        simple word
        "quoted words"
        "an embedded \"quote\" and an escaped \\ (backslash)"

    Note that semicolons will have to be URL-escaped before the query is passed
    in the URL.
    """
    _doubleBackslash = r'\\\\'
    _convertedDoubleBackslash = u'\u0560'
    _escaped = re.compile(_doubleBackslash)
    _unescaped = re.compile(_convertedDoubleBackslash)
    # .*? means non-greedy expansion, to avoid skipping over separators
    _startSep = re.compile(r'^(?P<head>.*?)(?P<sep>(\(|\)|,|(?<!\\)"))(?P<tail>.*)$')
    _endQuote = re.compile(r'^(?P<head>.*?)(?P<sep>(?<!\\)")(?P<tail>.*)$')

    def scan(self, s):
        return self._split(s)

    @classmethod
    def _split(cls, code):
        # The stack contains only tree nodes. Literal nodes are added as
        # operands directly to the last tree node in the stack.
        stack = []
        # First pass: we replace all double-backslashes with a
        # non-ascii unicode char, to simplify the regular expressions
        # _unescape will then revert this operation
        escCode = cls._escaped.sub(cls._convertedDoubleBackslash, code).strip()
        # There are only 2 states to worry about.
        # We look for a separator that is either ( , ) or " (unescaped,
        # hence the negative look-ahead in the regex)
        # If an (unescaped) quote is found, we need to find its matching
        # (unescaped) quote, which is the sep == '"' case.

        while escCode:
            m = cls._startSep.match(escCode)
            if m is None:
                raise InvalidData(msg="Unable to parse %s" % code)
            g = m.groupdict()
            head, sep, tail = g['head'], g['sep'], g['tail']
            # Get rid of leading whitespaces, unless the string is
            # quoted
            if sep != '"':
                escCode = tail.lstrip()
            else:
                escCode = tail
            if sep == '(':
                # New operator found.
                op = cls._unescape(head.strip()).upper()
                opFactory = operatorMap.get(op, None)
                if opFactory is None:
                    raise InvalidData(msg="Unknown operator %s" % op)
                tree = opFactory()
                if stack:
                    # Add the tree node to the parent (using the stack)
                    cls._addOperand(stack, tree)
                # ... and we push it onto the stack
                stack.append(tree)
                continue
            if sep == '"':
                # Ignore everything but a close quote
                m = cls._endQuote.match(escCode)
                if m:
                    g = m.groupdict()
                    head, sep, tail = g['head'], g['sep'], g['tail']
                    escCode = tail.lstrip()
                    cls._addOperand(stack, cls._unescapeString(head))
                    continue
                raise InvalidData(msg="Closing quote not found")
            if head:
                cls._addOperand(stack, cls._unescape(head.strip()))
            if sep == ',':
                continue
            assert sep == ')'
            top = stack.pop()
            if not stack:
                if escCode != '':
                    raise InvalidData(msg="Garbage found at the end of the expression: '%s'" % escCode)
                return top

    @classmethod
    def _addOperand(cls, stack, child):
        top = stack[-1]
        assert isinstance(top, Operator)
        top.addOperand(child)

    @classmethod
    def _unescape(cls, s):
        return cls._unescaped.sub(r'\\', s).encode('ascii')

    @classmethod
    def _unescapeString(cls, s):
        s = s.replace(r'\"', '"')
        return cls._unescape(s)

operatorMap = {}
for mod_obj in sys.modules[__name__].__dict__.values():
    if hasattr(mod_obj, 'filterTerm'):
        operatorMap[mod_obj.filterTerm] = mod_obj
