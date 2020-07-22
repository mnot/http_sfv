#!/usr/bin/python3

from http_sfv import List
my_list = List()
my_list.parse("foo; a=1, bar; b=2")

my_list
my_list[0]

my_list[0].value

my_list[0].params['a']

type(my_list[0].value)

from http_sfv import Token
my_list.append(Token('bar'))
my_list[-1]

from http_sfv import Dictionary
my_dictionary = Dictionary({'a': '1', 'b': 2, 'c': Token('foo')})
my_dictionary

my_dictionary['b'].params['b1'] = 2.0

print(my_dictionary)
