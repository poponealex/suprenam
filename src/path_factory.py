from pathlib import Path
from typing import NamedTuple
from random import choice
from string import ascii_lowercase
from path_siblings import get_path_siblings


class Scheme(NamedTuple):
    path: Path
    new_name: str


class Direction(NamedTuple):
    original_path: Path
    destination_path: Path


def create_temporary_filename(length: int = 15):
    return "".join(choice(ascii_lowercase) for _ in range(length))


def path_direction_factory(schemes: list[Scheme], arborescence: set[Path]) -> tuple[list[Direction], list[Direction]]:
    final_directions = []
    temporary_directions = []
    acc = set()
    for scheme in schemes:
        if scheme.path.name == scheme.new_name:
            final_directions.append(Direction(scheme.path, scheme.path))
            continue
        destination_path = Path(f"{scheme.path.parent}/{scheme.new_name}")
        acc.add(destination_path)
        if destination_path not in arborescence:
            final_directions.append(Direction(scheme.path, destination_path))
        elif destination_path in arborescence:
            while (temp_path := Path(f"{scheme.path.parent}/{create_temporary_filename()}")) in acc or temp_path in arborescence:
                continue
            acc.add(temp_path)
            temporary_directions.append(Direction(scheme.path, temp_path))
            final_directions.append(Direction(temp_path, destination_path))
    return (temporary_directions, final_directions)
