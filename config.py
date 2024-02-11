from pyBSDate import convert_BS_to_AD
import re

# categories = ['politics', 'kinmel',
#               'opinion', 'nepali-brand', 'social', 'art', 'blog', 'sports', 'global', 'cover-story']

categories = ['social']


nepali_months = {'वैशाख': 1,  'जेठ': 2, 'असार': 3, 'साउन': 4, 'भदौ': 5, 'असोज': 6,
                 'कात्तिक': 7, 'मंसिर': 8, 'पुस': 9, 'माघ': 10, 'फागुन': 11, 'चैत': 12}

nepali_years = {
    '२०७०': "2070", '२०७१': "2071", '२०७२': "2072",
    '२०७३': "2073", '२०७४': "2074", '२०७५': "2075",
    '२०७६': "2076", '२०७७': "2077", '२०७८': "2078",
    '२०७९': "2079", '२०८०': "2080", '२०८१': "2081",
    '२०८२': "2082",  '२०८३': "2083", '२०८४': "2084",
    '२०८५': "2085", '२०८६': "2086", '२०८७': "2087",
    '2088': "२०८८", '२०८९': "2089", '२०९०': "2090"
}

nepali_days = {
    '१': "1", '२': "2", '३': "3", '४': "4", '५': "5", '६': "6",
    '७': "7", '८': "8", '९': "9", '१०': "10", '११': "11", '१२': "12",
    '१३': "13", '१४': "14", '१५': "15", '१६': "16", '१७': "17", '१८': "18",
    '१९': "19", '२०': "20", '२१': "21", '२२': "22", '२३': "23", '२४': "24",
    '२५': "25", '२६': "26", '२७': "27", '२८': "28", '२९': "29", '३०': "30",
    '३१': "31", '३२': "32"
}

# clean date text by removing unecessary text


def extract_date(text):
    date_pattern = re.compile(r'प्रकाशित मिति: (.+?)$')
    match = re.search(date_pattern, text)
    if match:
        date = match.group(1)
        return date


def convert_to_english(date):
    nepali_date = extract_date(date)
    # regex to separate day month and year
    pattern = re.compile(
        r'([\u0900-\u097F]+), ([\u0900-\u097F]+) (\d+), (\d+)')

    match = re.search(pattern, nepali_date)

    if match:
        month = match.group(2)
        day = match.group(3)
        year = match.group(4)

        # convert to english font
        eng_day = nepali_days[day]
        eng_month = nepali_months[month]
        eng_year = nepali_years[year]

        # convert BS date to AD date
        ad_date = convert_BS_to_AD(eng_year, eng_month, eng_day)
        return f"{ad_date[0]}/{ad_date[1]}/{ad_date[2]}"
