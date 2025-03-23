import requests
from datetime import datetime
from .models import *


def get_nav_amfi(scheme_code):
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    response = requests.get(url)
    data = response.text.split("\n")

    for line in data:
        columns = line.split(";")
        if len(columns) > 4 and columns[0].strip() == scheme_code:
            return float(columns[4].strip())  # NAV is in the 5th column

    return None  # Scheme code not found

def update_sip_nav(sip):
    nav = get_nav_amfi(sip.scheme_code)
    if nav:
        sip.current_nav = nav
        sip.save()

        # Save NAV history for trend chart
        SIPNAVHistory.objects.create(
            sip=sip,
            date=datetime.today().date(),
            nav=nav
        )





