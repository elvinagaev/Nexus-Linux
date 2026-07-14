from dataclasses import dataclass


@dataclass(frozen=True)
class NexusApplicationInfo:
    name: str
    slug: str
    description: str
    category: str


class NexusApplication:
    def __init__(self, info: NexusApplicationInfo):
        self.info = info

    def run(self) -> None:
        print(f"{self.info.name} is ready for Qt6/PySide6 development.")
