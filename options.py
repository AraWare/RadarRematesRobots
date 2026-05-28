from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Options:
    url_to_bulletin_list_site: str
    url_to_bulletin_site: str
    number_of_bulletins_to_scrape: int

    @classmethod
    def from_json_file(cls, file_path: Path) -> "Options":
        with file_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "Options":
        url_to_bulletin_list_site = config.get("urlToBulletinListSite")
        url_to_bulletin_site = config.get("urlToBulletinSite")
        number_of_bulletins_to_scrape = config.get("numberOfBulletinsToScrape")

        if not isinstance(url_to_bulletin_list_site, str) or not url_to_bulletin_list_site.strip():
            raise ValueError("urlToBulletinListSite must be a non-empty string.")

        if not isinstance(url_to_bulletin_site, str) or not url_to_bulletin_site.strip():
            raise ValueError("urlToBulletinSite must be a non-empty string.")

        if not isinstance(number_of_bulletins_to_scrape, int) or number_of_bulletins_to_scrape < 1:
            raise ValueError("numberOfBulletinsToScrape must be an integer greater than or equal to 1.")

        return cls(
            url_to_bulletin_list_site=url_to_bulletin_list_site,
            url_to_bulletin_site=url_to_bulletin_site,
            number_of_bulletins_to_scrape=number_of_bulletins_to_scrape,
        )

    def bulletin_site_url(self, document_search_id: str) -> str:
        return self.url_to_bulletin_site.format(documentSearchId=document_search_id)
