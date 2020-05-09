from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import traceback
import os

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from config import data_dir, chrome_driver_dir

offer_info_desc = ['location', 'period', 'mode']
units_info = []

f = open(os.path.join(data_dir, 'fit_code.txt'))
code_ls = [line for line in f]
f.close()

# continue from previous scrapping
try:
    with open(os.path.join(data_dir, 'raw.json')) as f:
        units_info = json.load(f)
except Exception:
    units_info = []
code_ls = code_ls[len(units_info):]

driver = webdriver.Chrome(chrome_driver_dir)

for code in code_ls:

    driver.get("https://handbook.monash.edu/2020/units/" + str(code))
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

driver.quit()


with open(os.path.join(data_dir, 'raw.json'), 'w') as f:
    json.dump(units_info, f, indent=4)


