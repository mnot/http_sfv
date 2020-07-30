
# HTTP Structured Field Values in Python

[![Actions Status](https://github.com/mnot/http_sfv/workflows/CI/badge.svg)](https://github.com/mnot/http_sfv/actions)

This is a [Python 3](https://python.org/) library implementing parsing and serialisation of [HTTP Structured Fields](https://httpwg.org/http-extensions/draft-ietf-httpbis-header-structure.html).

The library's initial purpose is to prove the algorithms in the specification; as a result, it is not at all optimised. It tracks the specification closely, but since it is not yet an RFC, may change at any time.

_Currently, this implements draft 19 of the specification._

## Python API

There are three top-level types for Structured Field Values; `Dictionary`, `List` and `Item`. After instantiation, each can be used to parse a string HTTP header field value by calling `.parse()`:

~~~ python
>>> from http_sfv import List
>>> my_list = List()
>>> my_list.parse(b"foo; a=1, bar; b=2")
~~~

Note that `.parse()` takes a bytes-like object. If you want to parse a string, please `.encode()` it first.

Members of Lists and Dictionaries are available by normal Pythonic list and dictionary methods, respectively:

~~~ python
>>> my_list
[<http_sfv.item.Item object at 0x106d25190>, <http_sfv.item.Item object at 0x106d25210>]
>>> my_list[0]
<http_sfv.item.Item object at 0x106d25190>
~~~

Items (whether top-level or inside a list or dictionary value) can have their values accessed with the `.value` property:

~~~ python
>>> my_list[0].value
'foo'
~~~

Parameters on Items (and Inner Lists) can be accessed using the `.params` property, which is a dictionary:

~~~ python
>>> my_list[0].params['a']
1
~~~

Note that Tokens and Strings both evaluate as Python strings, but Tokens have a different class:

~~~ python
>>> type(my_list[0].value)
<class 'http_sfv.token.Token'>
~~~

That means that you need to create Tokens explicitly:

~~~ python
>>> from http_sfv import Token
>>> my_list.append(Token('bar'))
>>> my_list[-1]
'bar'
~~~

If you compare two Items, they'll be considered to be equivalent if their values match, even when their parameters are different:

~~~ python
>>> Token('foo') in my_list  # note that my_list's 'foo' has a parameter
True
>>> my_list.count(Token("foo"))
1
~~~

Inner Lists can be added by passing a list:

~~~ python
>>> my_list.append(['another_thing', 'and_another'])
>>> print(my_list)
foo;a=1, bar;b=2, bar, ("another_thing" "and_another")
>>> my_list[-1][-1].params['a'] = True
~~~

Dictionaries, Lists, and Items can be instantiated with a value:

~~~ python
>>> from http_sfv import Dictionary
>>> my_dictionary = Dictionary({'a': '1', 'b': 2, 'c': Token('foo')})
>>> my_dictionary
{'a': <http_sfv.item.Item object at 0x106a94c40>, 'b': <http_sfv.item.Item object at 0x106a94d00>, 'c': <http_sfv.item.Item object at 0x106a94dc0>}
~~~

Once instantiated, parameters can then be accessed:

~~~ python
>>> my_dictionary['b'].params['1'] = 2.0
~~~

Finally, to serialise a field value, just evaluate it as a string:

~~~ python
>>> print(my_dictionary)
a=1, b=2;b1=2.0, c=foo
~~~


## Command Line Use

You can validate and examine the data model of a field value by calling the library on the command line, using `-d`, `-l` and `-i` to denote dictionaries, lists or items respectively; e.g.,

~~~ example
> python3 -m http_sfv -i "foo;bar=baz"
[
    {
        "__type": "token",
        "value": "foo"
    },
    {
        "bar": {
            "__type": "token",
            "value": "baz"
        }
    }
]
~~~

or:

~~~ example
> python3 -m http_sfv -i "foo;&bar=baz"
FAIL: Key does not begin with lcalpha or * at: &bar=baz
~~~

Note that if successful, the output is in the JSON format used by the [test suite](https://github.com/httpwg/structured-header-tests/).
