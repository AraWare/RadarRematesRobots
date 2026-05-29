from datetime import datetime
import json
import re
from robocorp.tasks import task
from robocorp import browser
from bs4 import BeautifulSoup
from configuration_options.judicial_bulletin_options import judicial_bulletin_options
page = browser.page()



@task
def judicial_bulletin_extraction_robot():

    browser.configure(
        slowmo=100
    )

    open_website(judicial_bulletin_options.url_to_bulletin_list_site)

    bulletin_id_list = gather_the_ids_of_all_bulletins_in_the_list()

    bulletin_document_list = extracts_the_document_from_all_bulletins(bulletin_id_list)

    bulletin_auction_list = extracts_the_auctions_from_all_documents(bulletin_document_list)

    #write_the_bulletin_auctions_in_the_database(bulletin_auction_list)

    write_the_bulletin_auctions_in_a_json_file(bulletin_auction_list)

def open_website(url):
    page.goto(url)

def gather_the_ids_of_all_bulletins_in_the_list(): 
    
    page.wait_for_selector("div[ng-repeat='result in results']")
    results_locator = page.locator("div[ng-repeat='result in results']")
    results_to_process = results_locator.all()[:judicial_bulletin_options.number_of_bulletins_to_scrape]

    bulletin_id_list = []

    for result in results_to_process:

        document_id = result.locator("div.document-id").get_attribute("title")
        bulletin_number = result.locator("#result-title").inner_text()
    
        bulletin_id_list.append({
        "BulletinSearchId": document_id,
        "BulletinNumber": bulletin_number,
        })
    
    return bulletin_id_list

def extracts_the_document_from_all_bulletins(bulletin_id_list):

    bulletin_document_list = []

    for bulletin_id in bulletin_id_list:
        open_website(judicial_bulletin_options.bulletin_site_url(bulletin_id['BulletinSearchId']))
        page.wait_for_selector("#document")
        bulletin_document = page.inner_html("#document")

        bulletin_document_list.append({
        "BulletinSearchId": bulletin_id['BulletinSearchId'],
        "BulletinNumber": bulletin_id['BulletinNumber'],
        "BulletinDocument": bulletin_document
        })

    return bulletin_document_list

def is_section_title(p_tag):
    #Return True if this <p> looks like a section title.
    style = (p_tag.get("style") or "").lower()
    if "text-align:center" not in style:
        return False

    # Has a bold span inside?
    bold_span = p_tag.find("span", style=lambda s: s and "font-weight:bold" in s.lower())
    return bold_span is not None

def extract_auction_paragraphs_helper(html):
    soup = BeautifulSoup(html, "html.parser")

    # 1. Find the <p> that contains "REMATES PODER JUDICIAL"
    title_paragraph = soup.find("p", string=lambda t: t and "REMATES PODER JUDICIAL" in t)
    if not title_paragraph:
        return []  # this bulletin has no remates section

    auction_paragraphs = []

    for paragraph in title_paragraph.find_next_siblings("p"):
        # Stop when we reach the next section title
        if is_section_title(paragraph):
            break

        # Get clean text from paragraph
        paragraph_text = " ".join(paragraph.get_text(strip=True).split())
        if paragraph_text:  # skip empty lines
            auction_paragraphs.append(paragraph_text)

    return auction_paragraphs

def pair_auctions_with_reference(auction_list):
    reference_match_regex = r"Referencia\s*N°:\s*([0-9]+)"
    publication_match_regex = r"publicación\s*número:\s*([0-9]+\s+de\s+[0-9]+)"
    paired = []

    for i in range(0, len(auction_list), 2):
        auction = auction_list[i]
        reference_and_publication = auction_list[i + 1] if i + 1 < len(auction_list) else None
        reference_number = ''
        publication = ''

        if isinstance(reference_and_publication, str):
            reference_match = re.search(reference_match_regex, reference_and_publication, re.IGNORECASE)
            publication_match = re.search(publication_match_regex, reference_and_publication, re.IGNORECASE)

            if reference_match:
                reference_number = reference_match.group(1)
            if publication_match:
                publication = publication_match.group(1)

        paired.append({"Reference": reference_number, "Publication": publication, "Auction":auction})

    return paired

def extracts_the_auctions_from_all_documents(bulletin_document_list):

    bulletin_auction_list = []

    for bulletin_document in bulletin_document_list:
        auction_paragraphs = extract_auction_paragraphs_helper(bulletin_document['BulletinDocument'])
        referenced_auction_paragraphs = pair_auctions_with_reference(auction_paragraphs)

        bulletin_auction_list.append({
        "BulletinSearchId": bulletin_document['BulletinSearchId'],
        "BulletinNumber": bulletin_document['BulletinNumber'],
        "BulletinDocument": bulletin_document['BulletinDocument'],
        "BulletinAuctions": referenced_auction_paragraphs
        })

    return bulletin_auction_list

def write_the_bulletin_auctions_in_a_json_file(bulletin_auction_list):
    filename = "output/auctions/auctions-extracted-on-{}.json".format(datetime.now().strftime("%Y-%m-%dT%H-%M"))
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bulletin_auction_list, f, ensure_ascii=False, indent=2)

def write_the_bulletin_auctions_in_the_database(bulletin_auction_list):
    pass
