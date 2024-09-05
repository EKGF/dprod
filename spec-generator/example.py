from dataclasses import dataclass


@dataclass
class Example:
    name: str
    description: str = ''
    text: str = ''
    json: str = ''

