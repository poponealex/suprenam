from create_fhs import create_fhs
from path_siblings import get_path_siblings
from pathlib import Path


create_fhs()


assert get_path_siblings(set([Path("FHS/bin")])) == get_path_siblings(set([Path("FHS/boot")])) == get_path_siblings(set([Path("FHS/lib")])) == get_path_siblings(set([Path("FHS/var")])) 
assert get_path_siblings(set([Path("FHS/etc/X11/applnk")])) == get_path_siblings(set([Path("FHS/etc/X11/sysconfig")])) == get_path_siblings(set([Path("FHS/etc/X11/starthere")]))
assert get_path_siblings(set([Path("FHS/etc/opt")])) == get_path_siblings(set([Path("FHS/etc/skel")])) == get_path_siblings(set([Path("FHS/etc/sysconfig")]))
assert get_path_siblings(set([Path("FHS/mnt/cdrom")])) == get_path_siblings(set([Path("FHS/mnt/floppy")]))
assert get_path_siblings(set([Path("FHS/usr/X11R6")])) == get_path_siblings(set([Path("FHS/usr/bin")])) == get_path_siblings(set([Path("FHS/usr/games")]))
assert get_path_siblings(set([Path("FHS/usr/X11R6/bin")])) == get_path_siblings(set([Path("FHS/usr/X11R6/lib")]))
assert get_path_siblings(set([Path("FHS/usr/local/bin")])) == get_path_siblings(set([Path("FHS/usr/local/games")])) == get_path_siblings(set([Path("FHS/usr/local/sbin")])) == get_path_siblings(set([Path("FHS/usr/local/libexec")]))
assert get_path_siblings(set([Path("FHS/usr/local/share/man/man1")])) == get_path_siblings(set([Path("FHS/usr/local/share/man/man3")])) == get_path_siblings(set([Path("FHS/usr/local/share/man/man5")]))
assert get_path_siblings(set([Path("FHS/usr/share/dict")])) == get_path_siblings(set([Path("FHS/usr/share/empty")])) == get_path_siblings(set([Path("FHS/usr/share/misc")]))
assert get_path_siblings(set([Path("FHS/var/cache")])) == get_path_siblings(set([Path("FHS/var/empty")])) == get_path_siblings(set([Path("FHS/var/lib")]))
assert get_path_siblings(set([Path("FHS/var/lib/games")])) == get_path_siblings(set([Path("FHS/var/lib/misc")]))
assert get_path_siblings(set([Path("FHS/var/lib/games"), Path("FHS/var/cache")])) == get_path_siblings(set([Path("FHS/var/lib/misc"), Path("FHS/var/lib")]))
assert get_path_siblings(set([Path("FHS/usr/local/bin"), Path("FHS/mnt/cdrom")])) == get_path_siblings(set([Path("FHS/usr/local/games"), Path("FHS/mnt/floppy")]))
assert get_path_siblings(set([Path("FHS/bin"), Path("FHS/etc/X11/sysconfig")])) == get_path_siblings(set([Path("FHS/var"), Path("FHS/etc/X11/starthere")]))
assert len(get_path_siblings(set([Path("FHS/usr/X11R6/lib/tls")]))) == 1
assert len(get_path_siblings(set([Path("FHS/usr/local/share/man/man1")]))) == 10
assert len(get_path_siblings(set([Path("FHS/usr/share/man/man1")]))) == 10
assert len(get_path_siblings(set([Path("FHS/bin")]))) == 16
