# pylox
Complete Python 3.10+ implementation of the Lox programming language from [Crafting Interpreters](https://craftinginterpreters.com/).

You can find some sample code under the `example_programs` directory.

### Some notes:

 - Requires python 3.10+ due to the use of pattern matching.
 - Type hinting is partially compelete, but mypy doesn't support pattern matching yet so I can't actually run the static checks.

## Additional Features:

I've added some additional features where I thought they would be useful. These should not interfere with the base specification of Lox. 

### 1) `assert` statements

I find these really useful for writing really lazy tests. They work identically to python:

```
assert <expression>
```

This will evaluate the expression and raise an error if it evaluates to something false-y (in Lox, this is only `false` or `nil`). It will also print the line number and the actual line of code which includes the `assert` statement:

For example, in `test_scripts/bonus_assertions.lox`:
```
// prints powers of 2 from 2 to 32, then raise an assertion error.
var a = 1;
for (;;){
    a = a * 2;
    print a; 
    assert a != 32;
}
```

```
> pylox test_scripts/bonus_assertions.lox
2.0
4.0
8.0
16.0
32.0
Assertion Error on line 5: 
 ->      assert a != 32;
```

### 2) Modulo operator (`%`)

This was provided as an additional exercise in the book.
```
> pylox
pylox > print 12 % 5;
2.0
```
