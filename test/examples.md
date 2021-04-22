- [Foreword](#foreword)
- [Accepted schemes](#accepted-schemes)
  - [Null renaming](#null-renaming)
    - [(Not) renaming a leaf](#not-renaming-a-leaf)
    - [(Not) renaming a folder](#not-renaming-a-folder)
  - [Trivial renaming](#trivial-renaming)
    - [Trivial renaming of a leaf](#trivial-renaming-of-a-leaf)
    - [Trivial renaming of a folder](#trivial-renaming-of-a-folder)
  - [Redundant renaming](#redundant-renaming)
    - [Redundant renaming of a leaf](#redundant-renaming-of-a-leaf)
    - [Redundant renaming of a folder](#redundant-renaming-of-a-folder)
  - [Shifting](#shifting)
    - [Shifting the names of two leaves](#shifting-the-names-of-two-leaves)
    - [Shifting the names of one leaf and one folder](#shifting-the-names-of-one-leaf-and-one-folder)
    - [Shifting the names of one folder and one leaf](#shifting-the-names-of-one-folder-and-one-leaf)
    - [Shifting the names of two folders](#shifting-the-names-of-two-folders)
  - [Swapping](#swapping)
    - [Swapping the names of two leaves](#swapping-the-names-of-two-leaves)
    - [Swapping the names of a leaf and a folder](#swapping-the-names-of-a-leaf-and-a-folder)
    - [Swapping the names of two folders](#swapping-the-names-of-two-folders)
  - [Rolling](#rolling)
    - [Rolling the names of three leaves](#rolling-the-names-of-three-leaves)
    - [Rolling the names of two leaves and a folder](#rolling-the-names-of-two-leaves-and-a-folder)
    - [Rolling the names of one leaf and two folders](#rolling-the-names-of-one-leaf-and-two-folders)
    - [Rolling the names of three folders](#rolling-the-names-of-three-folders)
- [Rejected schemes](#rejected-schemes)
  - [Name clash among renaming clauses](#name-clash-among-renaming-clauses)
    - [Giving the same leaf at least two distinct names](#giving-the-same-leaf-at-least-two-distinct-names)
    - [Giving the same folder at least two distinct names](#giving-the-same-folder-at-least-two-distinct-names)
    - [Giving two distinct sibling leaves the same name](#giving-two-distinct-sibling-leaves-the-same-name)
    - [Giving two distinct sibling leaf and folder the same name](#giving-two-distinct-sibling-leaf-and-folder-the-same-name)
    - [Giving two distinct sibling folders the same name](#giving-two-distinct-sibling-folders-the-same-name)
  - [Name clash outside renaming clauses](#name-clash-outside-renaming-clauses)
    - [Giving a leaf the name of an existing leaf](#giving-a-leaf-the-name-of-an-existing-leaf)
    - [Giving a leaf the name of an existing folder](#giving-a-leaf-the-name-of-an-existing-folder)
    - [Giving a leaf the name of an existing folder renamed into itself](#giving-a-leaf-the-name-of-an-existing-folder-renamed-into-itself)
    - [Giving a folder the name of an existing leaf](#giving-a-folder-the-name-of-an-existing-leaf)
    - [Giving a folder the name of an existing folder](#giving-a-folder-the-name-of-an-existing-folder)

# Foreword

This text documents the result of the renaming of one or more nodes (leaf: either a file or a folder; internal node: a folder) of `fhs.txt` in a variety of normal cases and edge cases.

Moreover, it is parsed by `test_examples.py`, which runs the renaming algorithm on every example and checks the expected results. When an example consists in several renaming clauses, since their order is not important, all permutations of these clauses are automatically tested.

Note: to ensure formatting consistency, this file is updated by `reformat_examples.py` each time `test_examples.py` is launched.

# Accepted schemes

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

## Redundant renaming

--------------------------------------------------------------------------------

### Redundant renaming of a leaf

#### Example

original path | new name
---|---
/usr/libexec | foobar
/usr/libexec | foobar

#### Result

original path | new path
---|---
/usr/libexec | /usr/foobar

--------------------------------------------------------------------------------

### Redundant renaming of a folder

#### Example

original path | new name
---|---
/usr/lib | foobar
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

## Shifting

--------------------------------------------------------------------------------

### Shifting the names of two leaves

#### Example

original path | new name
---|---
/usr/local/share/man/man1 | man0
/usr/local/share/man/man2 | man1

#### Result

original path | new path
---|---
/usr/local/share/man/man1 | /usr/local/share/man/man0
/usr/local/share/man/man2 | /usr/local/share/man/man1

--------------------------------------------------------------------------------

### Shifting the names of one leaf and one folder

#### Example

original path | new name
---|---
/usr/local/share/info | spam
/usr/local/share/man | info

#### Result

original path | new path
---|---
/usr/local/share/info | /usr/local/share/spam
/usr/local/share/man | /usr/local/share/info
/usr/local/share/man/man1 | /usr/local/share/info/man1
/usr/local/share/man/man2 | /usr/local/share/info/man2
/usr/local/share/man/man3 | /usr/local/share/info/man3
/usr/local/share/man/man4 | /usr/local/share/info/man4
/usr/local/share/man/man5 | /usr/local/share/info/man5
/usr/local/share/man/man6 | /usr/local/share/info/man6
/usr/local/share/man/man7 | /usr/local/share/info/man7
/usr/local/share/man/man8 | /usr/local/share/info/man8
/usr/local/share/man/man9 | /usr/local/share/info/man9
/usr/local/share/man/mann | /usr/local/share/info/mann

--------------------------------------------------------------------------------

### Shifting the names of one folder and one leaf

#### Example

original path | new name
---|---
/usr/local/share/man | spam
/usr/local/share/info | man

#### Result

original path | new path
---|---
/usr/local/share/man | /usr/local/share/spam
/usr/local/share/man/man1 | /usr/local/share/spam/man1
/usr/local/share/man/man2 | /usr/local/share/spam/man2
/usr/local/share/man/man3 | /usr/local/share/spam/man3
/usr/local/share/man/man4 | /usr/local/share/spam/man4
/usr/local/share/man/man5 | /usr/local/share/spam/man5
/usr/local/share/man/man6 | /usr/local/share/spam/man6
/usr/local/share/man/man7 | /usr/local/share/spam/man7
/usr/local/share/man/man8 | /usr/local/share/spam/man8
/usr/local/share/man/man9 | /usr/local/share/spam/man9
/usr/local/share/man/mann | /usr/local/share/spam/mann
/usr/local/share/info | /usr/local/share/man

--------------------------------------------------------------------------------

### Shifting the names of two folders

#### Example

original path | new name
---|---
/usr/bin | spam
/usr/lib | bin

#### Result

original path | new path
---|---
/usr/bin | /usr/spam
/usr/bin/X11 | /usr/spam/X11
/usr/lib | /usr/bin
/usr/lib/X11 | /usr/bin/X11
/usr/lib/games | /usr/bin/games
/usr/lib/gcc-lib | /usr/bin/gcc-lib
/usr/lib/locale | /usr/bin/locale
/usr/lib/tls | /usr/bin/tls

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
/usr/share/man/man1 | man2
/usr/share/man/man2 | man3
/usr/share/man/man3 | man1

#### Result

original path | new path
---|---
/usr/share/man/man1 | /usr/share/man/man2
/usr/share/man/man2 | /usr/share/man/man3
/usr/share/man/man3 | /usr/share/man/man1

--------------------------------------------------------------------------------

### Rolling the names of two leaves and a folder

#### Example

original path | new name
---|---
/usr/bin | games
/usr/etc | bin
/usr/games | etc

#### Result

original path | new path
---|---
/usr/bin | /usr/games
/usr/bin/X11 | /usr/games/X11
/usr/etc | /usr/bin
/usr/games | /usr/etc

--------------------------------------------------------------------------------

### Rolling the names of one leaf and two folders

#### Example

original path | new name
---|---
/usr/X11R6 | games
/usr/bin | X11R6
/usr/games | bin

#### Result

original path | new path
---|---
/usr/X11R6 | /usr/games
/usr/X11R6/bin | /usr/games/bin
/usr/X11R6/include | /usr/games/include
/usr/X11R6/lib | /usr/games/lib
/usr/X11R6/lib/tls | /usr/games/lib/tls
/usr/X11R6/man | /usr/games/man
/usr/X11R6/share | /usr/games/share
/usr/bin | /usr/X11R6
/usr/bin/X11 | /usr/X11R6/X11
/usr/games | /usr/bin

--------------------------------------------------------------------------------

### Rolling the names of three folders

#### Example

original path | new name
---|---
/usr/X11R6 | lib
/usr/bin | X11R6
/usr/lib | bin

#### Result

original path | new path
---|---
/usr/X11R6 | /usr/lib
/usr/X11R6/bin | /usr/lib/bin
/usr/X11R6/include | /usr/lib/include
/usr/X11R6/lib | /usr/lib/lib
/usr/X11R6/lib/tls | /usr/lib/lib/tls
/usr/X11R6/man | /usr/lib/man
/usr/X11R6/share | /usr/lib/share
/usr/bin | /usr/X11R6
/usr/bin/X11 | /usr/X11R6/X11
/usr/lib | /usr/bin
/usr/lib/X11 | /usr/bin/X11
/usr/lib/games | /usr/bin/games
/usr/lib/gcc-lib | /usr/bin/gcc-lib
/usr/lib/locale | /usr/bin/locale
/usr/lib/tls | /usr/bin/tls

# Rejected schemes

## Name clash among renaming clauses

--------------------------------------------------------------------------------

### Giving the same leaf at least two distinct names

#### Example

original path | new name
---|---
/bin | trash
/bin | boom

#### Result

`SourceHasMultipleTargetsError("/bin")`

--------------------------------------------------------------------------------

### Giving the same folder at least two distinct names

#### Example

original path | new name
---|---
/etc | etera
/etc | esc

#### Result

`SourceHasMultipleTargetsError("/etc")`

--------------------------------------------------------------------------------

### Giving two distinct sibling leaves the same name

#### Example

original path | new name
---|---
/usr/lib/X11 | foobar
/usr/lib/games | foobar

#### Result

`TargetHasMultipleSourcesError("/usr/lib/foobar")`

--------------------------------------------------------------------------------

### Giving two distinct sibling leaf and folder the same name

#### Example

original path | new name
---|---
/usr/include | foobar
/usr/lib | foobar

#### Result

`TargetHasMultipleSourcesError("/usr/foobar")`

--------------------------------------------------------------------------------

### Giving two distinct sibling folders the same name

#### Example

original path | new name
---|---
/usr/bin | foobar
/usr/lib | foobar

#### Result

`TargetHasMultipleSourcesError("/usr/foobar")`

## Name clash outside renaming clauses

--------------------------------------------------------------------------------

### Giving a leaf the name of an existing leaf

#### Example

original path | new name
---|---
/usr/share/man/man1 | man2

#### Result

`TargetHasMultipleSourcesError("/usr/share/man/man2")`

--------------------------------------------------------------------------------

### Giving a leaf the name of an existing folder

#### Example

original path | new name
---|---
/opt | mnt

#### Result

`TargetHasMultipleSourcesError("/mnt")`

--------------------------------------------------------------------------------

### Giving a leaf the name of an existing folder renamed into itself

#### Example

original path | new name
---|---
/opt | mnt
/mnt | mnt

#### Result

`TargetHasMultipleSourcesError("/mnt")`

--------------------------------------------------------------------------------

### Giving a folder the name of an existing leaf

#### Example

original path | new name
---|---
/mnt | opt

#### Result

`TargetHasMultipleSourcesError("/opt")`

--------------------------------------------------------------------------------

### Giving a folder the name of an existing folder

#### Example

original path | new name
---|---
/lib | mnt

#### Result

`TargetHasMultipleSourcesError("/mnt")`
