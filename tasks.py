from robocorp.tasks import task
from robocorp import browser


#https://nexuspj.poder-judicial.go.cr/document/avi-1-0155-14256 Para abrir documentos
@task
def robot_boletines_poderjudicial():
    """Extracts the bulletins regarding judicial auctions."""

    browser.configure(
        slowmo=100
    )

    open_the_website()

    gather_the_ids_of_all_bulletins_in_the_list()

def open_the_website():
    browser.goto('https://nexuspj.poder-judicial.go.cr/search?q=tipoInformacion:(Bolet%C3%ADn%20AND%20Judicial)%20&advanced=true')

def gather_the_ids_of_all_bulletins_in_the_list():
    page = browser.page()
    page.wait_for_selector("div[ng-repeat='result in results']")
    results_locator = page.locator("div[ng-repeat='result in results']")

    bulletinList = []

    for result in results_locator.all():

        document_id = result.locator("div.document-id").get_attribute("title")
        bulletin_Number = result.locator("#result-title").inner_text()
    
        bulletinList.append({
        "BulletinSearchId": document_id,
        "BulletinNumber": bulletin_Number,
        })
    
    a = "a"
