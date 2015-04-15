from robobrowser import RoboBrowser
import datetime
import nameparser


def convert_date(date):
    return datetime.datetime.strptime(date, '%m/%d/%y').strftime("%Y-%m-%dT%H:%M:%S") + '.000Z'

def convert_name(name):
    parsed = nameparser.HumanName(name)
    return parsed.first, parsed.last


def search(fencer):
    browser = RoboBrowser()
    url = 'https://www.railstation.org/USFencing/MemberList.aspx?noheader=1'
    browser.open(url)
    f = browser.get_forms()[0]
    search_button = f.submit_fields['ctl00$ContentPlaceHolder$btnSearch']
    f['ctl00$ContentPlaceHolder$txtLastName'].value = fencer
    browser.submit_form(f, submit=search_button)

    browser.select('.ctl00_ContentPlaceHolder_grdMembers')
    table = browser.find('table', {'class':'grid'})
    headers = [cell.text.strip() for cell in table.find_all('th')]
    table = browser.find('table', {'class':'grid'})

    # fill in the rest of the columns that we know
    column_names = {"competitive", "division", "epee_rating", "expiration", "first_name", "foil_rating", "last_name", "membership_type", "Middle_Name", "representing_country", "saber_rating", "us_citizen"}
    print(headers)
    data = [col.text.strip() for row in table.find_all('tr', {'bgcolor':'White'}) for col in row.find_all('td')]
    print(data)
    column_names = ['name', 'member_number', 'division', 'representing_country', 'saber_rating', 'epee_rating', 'foil_rating', 'membership_type', 'expiration']
    res = dict(zip(column_names, data))
    res['expiration'] = convert_date(res['expiration'])

    first, last = convert_name(res.pop('name'))
    res['first_name'] = first
    res['last_name'] = last
    res['us_citizen'] = res['representing_country'] == 'USA'
    res['competitive'] = res['membership_type'] != 'Non-Competitive'
    number = res.pop('member_number')
    return {number: res}

if __name__ == '__main__':
    print(search('goller'))
