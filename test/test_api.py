#!/usr/bin/python3

from http_sfv import List, Token

my_list = List()
my_list.parse(b"foo; a=1, bar; b=2")

my_list
my_list[0]

assert(my_list[0].value == "foo")

assert(my_list[0].params['a'] == 1)
assert(type(my_list[0].value) == Token)

from http_sfv import Token
my_list.append(Token('bar'))
assert(my_list[-1].value == 'bar')
assert(type(my_list[-1].value) == Token)
assert(Token("foo") in my_list)
assert(my_list.count(Token("foo")) == 1)

my_list.append(['another_thing', 'and_another'])
assert(my_list[-1] == ['another_thing', 'and_another'])
my_list[-1][-1].params['a'] = True
print(my_list)

from http_sfv import Dictionary
my_dictionary = Dictionary({'a': '1', 'b': 2, 'c': Token('foo')})
my_dictionary

my_dictionary['b'].params['b1'] = 2.0

print(my_dictionary)
