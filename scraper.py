import requests
import bs4


def get_snow_report(search_url_loc):
    def extract_digits(digit_str):
        return ''.join(x for x in digit_str if x.isdigit() or x == '.' or x == '-')

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 " \
                 "Safari/537.36 "
    # US english
    language = "en-US,en;q=0.5"

    session = requests.Session()
    session.headers['User-Agent'] = user_agent
    session.headers['Accept-Language'] = language
    session.headers['Content-Language'] = language
    search_url = 'snow+report+' + search_url_loc
    html = session.get(url="https://www.google.com/search?q=" + search_url)

    soup = bs4.BeautifulSoup(html.text, "html.parser")

    result: dict = {
        "snowfall72": None,
        "snowfall48": None,
        "snowfall24": None,
        "snowDescription": None,
        "runsOpen": None,
        "liftsOpen": None,
        "base": None,
        "baseTemperature": None,
        "summit": None,
        "summitTemperature": None,
        "todaySnowForecast": None,
        "todayHighTemperature": None,
    }

    try:
        has_weather = bool(soup.find_all("td", attrs={"class": "cuG6ob"}))

        if has_weather:
            all_snowfall = soup.find_all("span", attrs={"class": "pjam0"})
            all_toplevel = soup.find_all("div", attrs={"class": "cuG6ob"})
            all_midlevel = soup.find_all("td", attrs={"class": "cuG6ob"})
            all_forecast_snow = soup.find_all("span", attrs={"class": "TSjJbc"})
            high_temperatures = soup.find_all("span", attrs={"class": "ZSvVgb"})

            if all_snowfall:
                result["snowfall72"] = extract_digits(all_snowfall[0].text)
                result["snowfall48"] = extract_digits(all_snowfall[1].text)
                result["snowfall24"] = extract_digits(all_snowfall[2].text)
            if all_toplevel:
                result["snowDescription"] = all_toplevel[0].text
                result["runsOpen"] = all_toplevel[1].text
                result["liftsOpen"] = all_toplevel[2].text
            if all_midlevel:
                result["base"] = extract_digits(all_midlevel[0].text)
                result["baseTemperature"] = extract_digits(all_midlevel[1].text)
                result["summit"] = extract_digits(all_midlevel[2].text)
                result["summitTemperature"] = extract_digits(all_midlevel[3].text)
            if all_forecast_snow:
                result["todaySnowForecast"] = extract_digits(all_forecast_snow[0].text)
            if high_temperatures:
                result["todayHighTemperature"] = extract_digits(high_temperatures[0].text)
            return result

        else:
            all_snowfall = soup.find_all("span", attrs={"class": "pjam0"})
            all_toplevel = soup.find_all("div", attrs={"class": "cuG6ob"})
            all_forecast_snow = soup.find_all("span", attrs={"class": "TSjJbc"})
            high_temperatures = soup.find_all("span", attrs={"class": "ZSvVgb"})

            if all_snowfall:
                result["snowfall72"] = extract_digits(all_snowfall[0].text)
                result["snowfall48"] = extract_digits(all_snowfall[1].text)
                result["snowfall24"] = extract_digits(all_snowfall[2].text)
            if all_toplevel:
                result["snowDescription"] = all_toplevel[0].text
                result["runsOpen"] = all_toplevel[1].text
                result["liftsOpen"] = all_toplevel[2].text
                result["base"] = extract_digits(all_toplevel[3].text)
                result["summit"] = extract_digits(all_toplevel[4].text)
            if all_forecast_snow:
                result["todaySnowForecast"] = extract_digits(all_forecast_snow[0].text)
            if high_temperatures:
                result["todayHighTemperature"] = extract_digits(high_temperatures[0].text)
            return result

    except IndexError:
        print("Valid snow report data not found for search url '{}'.".format(search_url))
        return result
