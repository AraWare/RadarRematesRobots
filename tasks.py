from robocorp.tasks import task
from robocorp import browser

@task
def robot_boletines_poderjudicial():
    """Extracts the bulletins regarding judicial auctions."""

    browser.configure(
        slowmo=100
    )

    open_the_website()

def open_the_website():
    browser.goto('https://nexuspj.poder-judicial.go.cr/search?q=tipoInformacion:(Bolet%C3%ADn%20AND%20Judicial)%20&advanced=true')
