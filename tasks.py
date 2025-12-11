from datetime import datetime
import json
from robocorp.tasks import task
from robocorp import browser
from bs4 import BeautifulSoup



urlToBulletinListSite = 'https://nexuspj.poder-judicial.go.cr/search?q=tipoInformacion:(Bolet%C3%ADn%20AND%20Judicial)%20&advanced=true' 
urlToBulletinSite = lambda documentSearchId: f"https://nexuspj.poder-judicial.go.cr/document/{documentSearchId}"
page = browser.page()
@task
def judicial_bulletin_extraction_robot():

    browser.configure(
        slowmo=100
    )

    open_website(urlToBulletinListSite)

    bulletinIdList = gather_the_ids_of_all_bulletins_in_the_list()

    bulletinDocumentList = extracts_the_document_from_all_bulletins(bulletinIdList)

    bulletinAuctionList = extracts_the_auctions_from_all_documents(bulletinDocumentList)

    writes_the_bulletin_auctions_in_a_json_file(bulletinAuctionList)

def open_website(url):
    page.goto(url)

def gather_the_ids_of_all_bulletins_in_the_list(): 
    
    page.wait_for_selector("div[ng-repeat='result in results']")
    resultsLocator = page.locator("div[ng-repeat='result in results']")

    bulletinIdList = []

    for result in resultsLocator.all():

        documentId = result.locator("div.document-id").get_attribute("title")
        bulletinNumber = result.locator("#result-title").inner_text()
    
        bulletinIdList.append({
        "BulletinSearchId": documentId,
        "BulletinNumber": bulletinNumber,
        })
    
    return bulletinIdList

def extracts_the_document_from_all_bulletins(bulletinIdList):

    bulletinDocumentList = []

    for bulletinId in bulletinIdList:
        open_website(urlToBulletinSite(bulletinId['BulletinSearchId']))
        page.wait_for_selector("#document")
        bulletinDocument = page.inner_html("#document")

        bulletinDocumentList.append({
        "BulletinSearchId": bulletinId['BulletinSearchId'],
        "BulletinNumber": bulletinId['BulletinNumber'],
        "BulletinDocument": bulletinDocument
        })

    return bulletinDocumentList

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
    titleParagraph = soup.find("p", string=lambda t: t and "REMATES PODER JUDICIAL" in t)
    if not titleParagraph:
        return []  # this bulletin has no remates section

    auctionParagraphs = []

    for paragraph in titleParagraph.find_next_siblings("p"):
        # Stop when we reach the next section title
        if is_section_title(paragraph):
            break

        # Get clean text from paragraph
        paragraphText = " ".join(paragraph.get_text(strip=True).split())
        if paragraphText:  # skip empty lines
            auctionParagraphs.append(paragraphText)

    return auctionParagraphs

def pair_auctions_with_reference(auction_list):
    paired = []
    for i in range(0, len(auction_list), 2):
        a = auction_list[i]
        b = auction_list[i + 1] if i + 1 < len(auction_list) else None
        paired.append({"Reference": b, "Auction":a})
    return paired


def extracts_the_auctions_from_all_documents(bulletinDocumentList):

    bulletinAuctionList = []

    for bulletinDocument in bulletinDocumentList:
        auctionParagraphs = extract_auction_paragraphs_helper(bulletinDocument['BulletinDocument'])
        referencedAuctionParagraphs = pair_auctions_with_reference(auctionParagraphs)

        bulletinAuctionList.append({
        "BulletinSearchId": bulletinDocument['BulletinSearchId'],
        "BulletinNumber": bulletinDocument['BulletinNumber'],
        "BulletinDocument": bulletinDocument['BulletinDocument'],
        "BulletinAuctions": referencedAuctionParagraphs
        })

    return bulletinAuctionList


def writes_the_bulletin_auctions_in_a_json_file(bulletinAuctionList):
    filename = "output/auctions/auctions-extracted-on-{}.json".format(datetime.now().strftime("%Y-%m-%dT%H-%M"))
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bulletinAuctionList, f, ensure_ascii=False, indent=2)


