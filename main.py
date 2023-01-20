import requests
import random
import csv
import re
import os
from googletrans import Translator

translator = Translator()

os.environ['GOOGLE_API_KEY'] = 'AIzaSyBi4Y4V0EadlXkw5f9Nq6LFOXVodB-OmRg'


def translate(text, lang='en'):
    return translator.translate(text, dest=lang).text


def remove_trailing_comma(value):
    return value.rstrip(",")


def convert_to_int(value):
    units = {"thousand": 1000, "million": 1000000, "billion": 1000000000}
    try:
        # remove any unit from the value
        for unit in units:
            value_stripped = remove_trailing_comma(value).replace(unit, "")
        # Use regex to extract numeric value from string
        numeric_value = re.search("[-+]?\d*\.\d+|\d+", value_stripped).group()
        # check if the value contains any unit
        for unit in units:
            if unit in value_stripped:
                numeric_value = float(numeric_value) * units[unit]
                break
        # Convert extracted value to int
        return int(numeric_value)
    except:
        print(f"Unable to convert {value} to int.")


def scrape_youtube_data(event, context=None):
    print(context)
    print(event)

    # Load the variables for search
    country = event['country']

    # Load country list
    country_list = [*csv.DictReader(open("assets/country_language.csv"))]
    country_dict = list(filter(lambda d: d['country_name'] == country, country_list))

    # Translate keyword
    keyword = translate(event['keyword'], lang=country_dict[0]['language_code'])

    # Configure proxy
    http_proxy = f"http://user-Growth:Thunders@{country_dict[0]['country_code']}.smartproxy.com:20000"
    proxies = {"http": http_proxy}
    params = {
        "hl": country_dict[0]['language_code'],
        "gl": country_dict[0]['country_code']
    }

    # Hit request with search query
    html = requests.get(f"https://www.youtube.com/results?search_query={keyword}",
                        cookies={'CONSENT': 'PENDING+{}'.format(random.randint(100, 999))},
                        proxies=proxies, params=params)

    # Get the uniquelist of videos
    videos = re.findall(r'/watch\?v=(.*?)","webPageType"', html.text)
    video_ids = list(set([v_id[0:11] for v_id in videos]))

    # Analyze the videos
    channel_id_list = []
    for vid_id in video_ids:
        try:
            #Clear variables
            channel_id = None

            # Get the request for video
            html = requests.get(f'https://www.youtube.com/watch?v={vid_id}',
                                cookies={'CONSENT': 'PENDING+{}'.format(random.randint(100, 999))},
                                proxies=proxies, params=params)

            # Get the channel id from video html
            try:
                channel_id = re.findall(r'],"channelId":"(.*?)","', html.text)[0]
            except Exception as e:
                print(e)
                channel_id = re.findall(r'"originalUrl": "https://www.youtube.com/channel/(.*?)","', html.text)[0]

            channel_id_list.append(channel_id)
        except Exception as e:
            print(e)

    channel_id_list_unique = list(set(channel_id_list))
    data = []
    for channel_id in channel_id_list_unique:
        try:
            # Get channel html
            html = requests.get(f'https://www.youtube.com/channel/{channel_id}/about',
                                cookies={'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+{}'.format(
                                    random.randint(100, 999))}, proxies=proxies, params=params)

            # Get the data from channel about html
            name = re.findall(r'{"title":"(.*?)","', html.text)[0]
            subs = convert_to_int(translate(re.findall(r'}},"simpleText":"(.*?)"tvBanner"', html.text)[0]).
                                  replace(" subscribers\"}", ""))
            channel_country = translate(re.findall(r'"country":{"simpleText":"(.*?)"},', html.text)[0])

            print(f"Channel link: https://www.youtube.com/channel/{channel_id}/about \n"
                  f"Name: {name} Subs: {subs} Country: {channel_country}")

            # Save to final output
            data.append({'channel_id': channel_id, 'name': name, 'subs': subs, 'country': channel_country})

        except Exception as e:
            print(e)

            try:
                print(f"Error Channel link: https://www.youtube.com/channel/{channel_id}/about")
            except:
                print(f'Error https://www.youtube.com/watch?v={vid_id}')
    return data


if __name__ == "__main__":
    scrape_youtube_data(event={"country": "Germany", "keyword": "Outdoor activities"})
