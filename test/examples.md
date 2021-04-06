- [Examples](#examples)
  - [Null renaming](#null-renaming)
    - [(Not) renaming a leaf](#not-renaming-a-leaf)
    - [(Not) renaming a folder](#not-renaming-a-folder)
  - [Trivial renaming](#trivial-renaming)
    - [Trivial renaming of a leaf](#trivial-renaming-of-a-leaf)
    - [Trivial renaming of a folder](#trivial-renaming-of-a-folder)
  - [Swapping](#swapping)
    - [Swapping the names of two leaves](#swapping-the-names-of-two-leaves)
    - [Swapping the names of a leaf and a folder](#swapping-the-names-of-a-leaf-and-a-folder)
    - [Swapping the names of two folders](#swapping-the-names-of-two-folders)
  - [Rolling](#rolling)
    - [Rolling the names of three leaves](#rolling-the-names-of-three-leaves)
    - [Rolling the names of two leaves and a folder](#rolling-the-names-of-two-leaves-and-a-folder)
    - [Rolling the names of one leaf and two folders](#rolling-the-names-of-one-leaf-and-two-folders)
    - [Rolling the names of three folders](#rolling-the-names-of-three-folders)
  - [Permuting (TODO)](#permuting-todo)

# Examples

This text documents the result of the renaming of one or more nodes (leaf: either a file or a folder; internal node: a folder) of `fhs.txt` in a variety of normal cases and edge cases.

Moreover, it is parsed by `test_examples.py`, which runs the renaming algorithm on every example and checks the expected results. When an example consists in several renaming clauses, since their order is not important, all permutations of these clauses are automatically tested.

Note: to ensure formatting consistency, this file is updated by `reformat_examples.py` each time `test_examples.py` is launched.

## Null renaming

--------------------------------------------------------------------------------

### (Not) renaming a leaf

#### Example

original path | new name
---|---
/usr/share/man/man1 | man1

#### Result

original path | new path
---|---

--------------------------------------------------------------------------------

### (Not) renaming a folder

#### Example

original path | new name
---|---
/usr/share/man | man

#### Result

original path | new path
---|---

## Trivial renaming

--------------------------------------------------------------------------------

### Trivial renaming of a leaf

#### Example

original path | new name
---|---
/usr/libexec | foobar

#### Result

original path | new path
---|---
/usr/libexec | /usr/foobar

--------------------------------------------------------------------------------

### Trivial renaming of a folder

#### Example

original path | new name
---|---
/usr/lib | foobar

#### Result

original path | new path
---|---
/usr/lib | /usr/foobar
/usr/lib/X11 | /usr/foobar/X11
/usr/lib/games | /usr/foobar/games
/usr/lib/gcc-lib | /usr/foobar/gcc-lib
/usr/lib/locale | /usr/foobar/locale
/usr/lib/tls | /usr/foobar/tls

## Swapping

--------------------------------------------------------------------------------

### Swapping the names of two leaves

#### Example

original path | new name
---|---
/usr/share/man/man1 | man2
/usr/share/man/man2 | man1

#### Result

original path | new path
---|---
/usr/share/man/man1 | /usr/share/man/man2
/usr/share/man/man2 | /usr/share/man/man1

--------------------------------------------------------------------------------

### Swapping the names of a leaf and a folder

#### Example

original path | new name
---|---
/usr/include | lib
/usr/lib | include

#### Result

original path | new path
---|---
/usr/include | /usr/lib
/usr/lib | /usr/include
/usr/lib/X11 | /usr/include/X11
/usr/lib/games | /usr/include/games
/usr/lib/gcc-lib | /usr/include/gcc-lib
/usr/lib/locale | /usr/include/locale
/usr/lib/tls | /usr/include/tls

--------------------------------------------------------------------------------

### Swapping the names of two folders

#### Example

original path | new name
---|---
/etc | lib
/lib | etc

#### Result

original path | new path
---|---
/etc | /lib
/etc/X11 | /lib/X11
/etc/X11/applnk | /lib/X11/applnk
/etc/X11/serverconfig | /lib/X11/serverconfig
/etc/X11/starthere | /lib/X11/starthere
/etc/X11/sysconfig | /lib/X11/sysconfig
/etc/opt | /lib/opt
/etc/skel | /lib/skel
/etc/sysconfig | /lib/sysconfig
/etc/xinetd.d | /lib/xinetd.d
/lib | /etc
/lib/modules | /etc/modules
/lib/tls | /etc/tls

## Rolling

--------------------------------------------------------------------------------

### Rolling the names of three leaves

#### Example

original path | new name
---|---
/usr/share/man/man1 | 1man
/usr/share/man/man2 | 2man
/usr/share/man/man3 | 3man

#### Result

original path | new path
---|---
/usr/share/man/man1 | /usr/share/man/1man
/usr/share/man/man2 | /usr/share/man/2man
/usr/share/man/man3 | /usr/share/man/3man

--------------------------------------------------------------------------------

### Rolling the names of two leaves and a folder

#### Example

original path | new name
---|---
/usr/share/man | nma
/usr/share/man/man1 | 1man
/usr/share/man/man2 | 2man

#### Result

original path | new path
---|---
/usr/share/man | /usr/share/nma
/usr/share/man/man1 | /usr/share/nma/1man 
/usr/share/man/man2 | /usr/share/nma/2man

--------------------------------------------------------------------------------

### Rolling the names of one leaf and two folders

#### Example

original path | new name
---|---
/usr/share/ | eshar
/usr/share/man/ | nma
/usr/share/man/man1 | 1man

#### Result

original path | new path
---|---
/usr/share/ | /usr/eshar
/usr/share/man/ | /usr/eshar/nma
/usr/share/man/man1 | /usr/eshar/nma/1man

--------------------------------------------------------------------------------

### Rolling the names of three folders

#### Example

original path | new name
---|---
/usr/ | rus
/usr/share/ | eshar
/usr/share/man/ | nma

#### Result

original path | new path
---|---
/usr/ | /rus
/usr/share/ | /rus/eshar
/usr/share/man/ | /rus/eshar/nma

## Permuting (TODO)

Enumerate all permutations of four nodes.