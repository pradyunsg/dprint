# dprint

A printing debugging helper.

## Motivation

`dprint` is inspired by a [python-ideas thread][1], to show what's possible 
with a little bit of magic with plain Python code.

## Installation

It's on PyPI as `dprint`. The obvious way will just work:

```
pip install dprint
```

## Usage

Import the function `dprint` from the `dprint` module.

```py
from dprint import dprint


def spam():
    eggs = 10
    dprint(eggs * 2)

spam()
```

Running the above script gives:

```
$ python script.py
script.py:6 in spam
  eggs * 2 -> 20
```

## Operational Assumptions

The current logic for figuring out the expression passed to dprint operates under some assumptions:

- The imported function must be called `dprint`
- A call should span no more than 1 line
- No more than 1 call on 1 line

A future version might relax these assumptions.

## License

All files in this repository are under the MIT license.

[1]: https://mail.python.org/pipermail/python-ideas/2018-April/050113.html
