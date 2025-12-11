from robocorp.tasks import task
from robocorp import browser


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

    extracts_the_information_from_all_bulletins(bulletinIdList)

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

def extracts_the_information_from_all_bulletins(bulletinIdList):

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


    