import re
import json
import requests
import wikipedia
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from country_list import countries_for_language

DEBUG = False

def parse_string(tag):
    if isinstance(tag, NavigableString):
        return str(tag.string)
    else:
        return tag.text

def get_party(link, country):
    uid = link.replace("https://en.wikipedia.org/wiki/", "")
    r = requests.get(link)
    soup = BeautifulSoup(r.content, features="lxml")
    infobox = soup.find("table", {"class":"infobox vcard"})

    if infobox is None:
        return None

    if not "Ideology" in str(infobox):
        return None

    name = infobox.find("div", class_="fn org")

    if name is None:
        return None

    rows = infobox.find("tbody")
    ideology_row = [row for row in rows if "ideology" in str(row).lower()]
    position_row = [row for row in rows if "position" in str(row).lower() and "opposition" not in str(row).lower()]

    ideology = []
    if len(ideology_row) > 0:
        ideology = [x for x in ideology_row[0].find("td")]

    #get the text as it appears
    td = ideology_row[0].find("td")

    if DEBUG:
        print(repr(td.get_text('\n')))

    for linebreak in td.find_all("br"):
        linebreak.extract()

    ideology_string = td.get_text('\n')

    #remove anything in brackets
    ideology_string = re.sub(r' ?\([^)]+\)', '', ideology_string)

    #remove citations
    #ideology_string = re.sub(r'\[[^)]+\]', '', ideology_string)
    ideology_string = re.sub(r'\[[0-9]*[a-z]*\]', '', ideology_string)
    ideology_string = re.sub(r'[\s]*\[[\s]*citation[\s]*needed[\s]*\][\s]*', ' ', ideology_string)

    ideology_string = re.sub(r'–', '-', ideology_string)
    ideology_string = re.sub(r'•', '', ideology_string)
    ideology_string = re.sub(r'[\s]+\'', '\'', ideology_string)

    #remove whitespace after anti / pro etc words
    ideology_string = re.sub(r'Anti-[\s]+', 'Anti-', ideology_string)
    ideology_string = re.sub(r'Pro-[\s]+', 'Pro-', ideology_string)
    ideology_string = re.sub(r'Ban on[\s]+', 'Pro-', ideology_string)
    ideology_string = re.sub(r'[\s]+politics', ' politics', ideology_string)
    ideology_string = re.sub(r'[\s]+for', ' for', ideology_string)
    ideology_string = re.sub(r'[\s]+of the[\s]+', ' of the ', ideology_string)
    ideology_string = re.sub(r'[\s]+regionalism', ' regionalism', ideology_string)
    ideology_string = re.sub(r'[\s]+nationalism', ' nationalism', ideology_string)
    ideology_string = re.sub(r'[\s]+ultranationalism', ' ultranationalism', ideology_string)
    ideology_string = re.sub(r'[\s]+fandom', ' fandom', ideology_string)
    ideology_string = re.sub(r'[\s]+democracy', ' democracy', ideology_string)
    ideology_string = re.sub(r'[\s]+conservatism', ' conservatism', ideology_string)
    ideology_string = re.sub(r'[\s]+devolution', ' devolution', ideology_string)
    ideology_string = re.sub("interest$", "interests", ideology_string)
    ideology_string = re.sub(r"[\s]+interest[^s]", " interests", ideology_string)
    ideology_string = re.sub(r'[\s]+interests', ' interests', ideology_string)
    ideology_string = re.sub(r'[\s]+loyalty', ' loyalty', ideology_string)
    ideology_string = re.sub(r'Factions[\s]*:', ' ', ideology_string)
    ideology_string = re.sub(r'Majority[\s]*:', ' ', ideology_string)

    if DEBUG:
        print(repr(ideology_string))

    #split into different lines
    ideology_string = re.sub("\n[\s]+\n", "\n\n", ideology_string)
    if DEBUG:
        print(repr(ideology_string))

    delim = "\n" if "\n\n" not in ideology_string else "\n\n"
    delim = "\n"
    ideology = ideology_string.split(delim)

    if DEBUG:
        print(ideology)

    #remove citations
    #ideology = [re.sub(r'\[[0-9]*\]', '', x) for x in ideology]

    #remove any whitespace
    ideology = [x.replace("\n", "") for x in ideology]
    ideology = [x.replace(u'\xa0', u' ') for x in ideology]
    ideology = [x for x in ideology if len(x) > 0]
    ideology = [str(x.strip()) for x in ideology if not x.isspace()]

    #position = []
    #if len(position_row) > 0:
    #    position = [link.text for link in position_row[0].find("td").find_all("a", href=True) if "cite" not in link["href"]]

    colors = [str(x) for x in set(re.findall(r'#[0-9a-f]{6}', str(infobox).lower()))]

    return {"id":str(uid), "name":str(name.contents[0].string), "ideology":ideology, "colors":colors, "country":country.lower()}

def get_all_parties():
    countries = dict(countries_for_language('en')).values()
    parties = []

    ids = set()
    for country in countries:
        get_parties_for_country(country)

def get_parties_for_country(country):
    print(country)
    ids = set()

    parties = []

    try:
        page = wikipedia.page("List of political parties in " + country)
        page_source = page.html()
        soup = BeautifulSoup(page_source, features="lxml")
        links = ["https://en.wikipedia.org" + link["href"] for link in soup.find_all("a", href=True) if link["href"].startswith("/wiki")]

        for link in links:
            party = get_party(link, country)

            if party is not None:
                if party["id"] not in ids:
                    ids.add(party["id"])
                    parties.append(party)
                    print(len(ids), str(party["name"]) + ": " + ", ".join(party["ideology"]))

        with open("data/" + country.replace(" ","_").lower() + ".json", "w") as fout:
            json.dump(parties, fout)

        print()

    except Exception as e:
        print(e)

#get_all_parties()
countries = ["United Kingdom", "United States", "Germany", "Japan", "Spain"]

for country in countries:
    get_parties_for_country(country)

def run_tests():
    print(get_party("https://en.wikipedia.org/wiki/Conservative_Party_(UK)"))
    print(get_party("https://en.wikipedia.org/wiki/Watan_Party_of_Afghanistan"))
    print(get_party("https://en.wikipedia.org/wiki/Popular_Front_for_the_Liberation_of_Palestine"))
    print(get_party("https://en.wikipedia.org/wiki/Palestinian_People%27s_Party"))
    print(get_party("https://en.wikipedia.org/wiki/Whigs_(British_political_party)"))
    print(get_party("https://en.wikipedia.org/wiki/Unionist_Party_(Scotland)"))
    print(get_party("https://en.wikipedia.org/wiki/Labour_Party_(UK)"))
    print(get_party("https://en.wikipedia.org/wiki/Agang_South_Africa"))
    print(get_party("https://en.wikipedia.org/wiki/Abolish_the_Welsh_Assembly_Party"))
    print(get_party("https://en.wikipedia.org/wiki/Mebyon_Kernow"))
    print(get_party("https://en.wikipedia.org/wiki/Church_of_the_Militant_Elvis_Party"))
    print(get_party("https://en.wikipedia.org/wiki/National_Health_Action_Party"))
    print(get_party("https://en.wikipedia.org/wiki/Irish_Unionist_Alliance"))
    print(get_party("https://en.wikipedia.org/wiki/Cornish_Nationalist_Party"))
    print(get_party("https://en.wikipedia.org/wiki/British_Union_of_Fascists"))
    print(get_party("https://en.wikipedia.org/wiki/South_African_Party"))
    print(get_party("https://en.wikipedia.org/wiki/United_Party_(South_Africa)"))
    print(get_party("https://en.wikipedia.org/wiki/Saenuri_Party_(2017)"))
    print(get_party("https://en.wikipedia.org/wiki/Liberty_Korea_Party"))
    print(get_party("https://en.wikipedia.org/wiki/Progressive_Party_(South_Korea,_1956)"))
    print(get_party("https://en.wikipedia.org/wiki/New_Progressive_Party_(South_Korea)"))
    print(get_party("https://en.wikipedia.org/wiki/Korea_Vision_Party"))
    print(get_party("https://en.wikipedia.org/wiki/Democratic_Party_(United_States)"))
    print(get_party("https://en.wikipedia.org/wiki/Citizens_Party_of_the_United_States"))
    print(get_party("https://en.wikipedia.org/wiki/Movimiento_Uni%C3%B3n_Soberanista"))
    print(get_party("https://en.wikipedia.org/wiki/Transport_Matters_Party"))
    print(get_party("https://en.wikipedia.org/wiki/Cooperation_and_Brotherhood"))
    print(get_party("https://en.wikipedia.org/wiki/Communist_Party_of_Germany_(Opposition)"))
    print(get_party("https://en.wikipedia.org/wiki/Liberal_Democratic_Party_(Japan)"))

#run_tests()
