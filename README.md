
# HTTP Structured Field Values in Python

[![Actions Status](https://github.com/mnot/http_sfv/workflows/CI/badge.svg)](https://github.com/mnot/http_sfv/actions)

This is a [Python 3](https://python.org/) library implementing parsing and serialisation of [HTTP Structured Fields](https://httpwg.org/http-extensions/draft-ietf-httpbis-header-structure.html).

The library's initial purpose is to prove the algorithms in the specification; as a result, it is not at all optimised. It tracks the specification closely, but since it is not yet an RFC, may change at any time.

_Currently, this implements [draft-ietf-httpbis-sfbis-03](https://datatracker.ietf.org/doc/draft-ietf-httpbis-sfbis/)._

## Python API

Textual HTTP headers can be parsed by calling `parse`; the return value is a data structure that represents the field value.

~~~ python
>>> from http_sfv import parse, ser
>>> parse(b"foo; a=1, bar; b=2", tltype="dictionary")
{'foo': (True, {'a': 1}), 'bar': (True, {'b': 2})}
~~~

Note that `.parse()` takes a bytes-like object as the first argument. If you want to parse a string, please `.encode()` it first.

Because the library needs to know which kind of field it is, you need to hint this when calling `parse`. There are two ways to do this:

1. Using a `tltype` parameter, whose value should be one of 'dictionary', 'list', or 'item'.
2. Using a `name` parameter to indicate a field name that has a registered type, per [the retrofit draft](https://httpwg.org/http-extensions/draft-ietf-httpbis-retrofit.html).

Note that if you use `name`, a `KeyError` will be raised if the type associated with the name isn't known.

Dictionaries are represented as Python dictionaries; Lists are represented as Python lists, and Items are represented using the following Python types:

* Integers: `int`
* Decimals: `float`
* Strings: `str`
* Tokens: `http_sfv.Token` (a `UserString`)
* Byte Sequences: `bytes`
* Booleans: `bool`
* Dates: `datetime.datetime`
* Display Strings: `http_sfv.DisplayString` (a `UserString`)

Inner Lists are represented as lists as well.

Structured Types that can have parameters (including Dictionary and List members as well as singular Items and Inner Lists) are represented as a tuple of `(value, parameters)` where parameters is a dictionary.

So, a single item that's a Token with one parameter whose value is an integer will be represented like this:

~~~ python
>>> parse(b"foo; a=1", tltype="item")
(Token("foo"), {'a': 1})
~~~

Note that even if there aren't parameters, a tuple will still be returned, as in soem items on this List:

~~~ python
>>> parse(b"a, b; q=5, c", tltype="list")
[(Token("a"), {}), (Token("b"), {'q': 5}), (Token("c"), {})]
~~~

To serialise that data structure back to a textual Structured Field, use `ser`:

~~~ python
>>> field = parse(b"a, b; q=5, c", tltype="list")
>>> ser(field)
'a, b;q=5, c'
~~~

When using `ser`, if an Item or Inner List doesn't have parameters, they can be omitted; for example:

~~~ python
>>> structure = [5, 6, (7, {"with": "param"})]
>>> ser(structure)
'5, 6, 7;with="param"'
~~~

However, `parse` will always produce tuples for Items and Inner Lists, even when there are no parameters:

~~~ python
>>> parse(bytes(ser(structure), encoding='ascii'), tltype='list')
[(5, {}), (6, {}), (7, {'with': 'param'})]
~~~

Note that `ser` produces a string, not a bytes-like object.
