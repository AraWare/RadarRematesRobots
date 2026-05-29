from dataclasses import dataclass, field
from auction import Auction


@dataclass
class BulletinAuction:
    BulletinSearchId: str
    BulletinNumber: str
    BulletinDocument: str = ""
    BulletinAuctions: list[Auction] = field(default_factory=list)
