from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import traceback

offer_info_desc = ['location', 'period', 'mode']
units_info = []

f = open('fit_code.txt')
code_ls = [line for line in f]
f.close()

try:
    with open('data.json') as f:
        units_info = json.load(f)
except Exception:
    units_info = []

code_ls = code_ls[len(units_info):]

driver = webdriver.Chrome("/Users/kx/chromedriver")

for  code in code_ls:
    code_str = str(code)
    driver.get("https://handbook.monash.edu/2020/units/" + code_str)
    time.sleep(5)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    unit = soup.find('h2', attrs={'class':'css-3hrxrh-Heading-ComponentHeading-Heading-css ezav15i5'})

    try:
        if unit is not None:
            unit_info = {}
            code_name = unit.text.split('-')
            unit_info['code'] = code_name[0].strip()
            unit_info['name'] = '-'.join(code_name[1:]).strip()
            unit_info['offers'] = []

            soup = BeautifulSoup(content, features="lxml")
            info = soup.findAll('div', attrs={'class':'css-ky59ff-SAccordionContentContainer e1450wuy9'})

            rule_i = -1
            for i, offer in enumerate(info):

                p = offer.find('p')
                if p is not None:
                    rule_i = i
                    break

                offer_info = {}
                ls = offer.findAll('div', attrs={'class':'css-16ojjq2-Box-CardBody e1q64pes0'})

                try:
                    for j in range(len(ls)):
                        label = ls[j].find('span', attrs={'class':'css-1nigt7g-SMainHeading e149fqi62'})
                        offer_info[offer_info_desc[j]] = label.next_sibling.strip()

                    unit_info['offers'].append(offer_info)

                except AttributeError:
                    rule_i = i
                    break

            unit_info['rule'] = info[i].text.strip()
            unit_info['credit_points'] = soup.findAll('h4')[-1].next_sibling.text.strip()
            units_info.append(unit_info)


        else:
            raise Exception("Unit not found")

    except Exception as e:
        print(code, e)
        traceback.print_exc()
        break

with open('data.json', 'w') as f:
    json.dump(units_info, f, indent=4)

driver.quit()
