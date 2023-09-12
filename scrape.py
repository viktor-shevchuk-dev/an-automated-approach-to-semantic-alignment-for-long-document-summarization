import os
from requests_html import AsyncHTMLSession
import pandas as pd

from helpers import *

asession = AsyncHTMLSession()
SLEEP_TIME = 10


async def get_English_laws_pagination_urls():
    English_laws_pagination_urls = [
        "https://zakon.rada.gov.ua/laws/main/en/llenglaws/page"]

    r = await asession.get(English_laws_pagination_urls[0])
    await r.html.arender()
    pagination_link_element_list = r.html.find(
        ".page-link:not([title='current page'])")

    for pagination_link_element in pagination_link_element_list:
        pagination_url = next(iter(pagination_link_element.absolute_links))
        English_laws_pagination_urls.append(pagination_url)

    return English_laws_pagination_urls


def save_document(element_list, documents_list_specifier):
    documents_list_directory = os.path.join(
        os.path.curdir, "english_laws_with_abstracts", documents_list_specifier)

    create_folder_if_not_exists(documents_list_directory)

    start_index = get_next_index(documents_list_directory)

    document_directory = os.path.join(documents_list_directory, start_index)
    os.mkdir(document_directory)

    para_index = 0
    for _, element in enumerate(element_list):
        if not element.text.strip():
            continue

        file_path = os.path.join(document_directory, f'{para_index}.txt')

        with open(file_path, 'w') as f:
            f.write(element.text)

        para_index += 1


async def retrieve_abstract(url):
    r = await asession.get(url)
    await r.html.arender(sleep=SLEEP_TIME)
    element_list = r.html.find(".rvts0 [align='justify'], .rvts0 ul")
    return element_list


async def retrieve_law_and_abstract(law_url):
    english_laws_and_abstracts_path = os.path.join(
        os.path.curdir, "english_laws_with_abstracts", "df.csv")
    df = pd.read_csv(english_laws_and_abstracts_path)

    if df['law_url'].str.contains(law_url).any():
        return

    row = {'law_url': law_url}

    r = await asession.get(law_url)
    await r.html.arender(sleep=SLEEP_TIME)
    abstract_icon = r.html.find("[title='Abstract']", first=True)

    if abstract_icon:
        law_element_list = r.html.find(
            ".rvts0 > .rvps8, .rvts0 > .rvps2, .rvts0 .rvts15")

        if law_element_list:
            abstract_link_element = r.html.find("[href*='anot']", first=True)
            row['abstract_url'] = next(
                iter(abstract_link_element.absolute_links))
            abstract_element_list = await retrieve_abstract(row['abstract_url'])
            save_document(law_element_list, 'laws')
            save_document(abstract_element_list, 'abstracts')
        else:
            row['is_standardized'] = False

    df.loc[len(df)] = row
    df.to_csv(english_laws_and_abstracts_path, index=False)


async def retrieve_page_from_pagination(url):
    r = await asession.get(url)
    await r.html.arender()
    laws_link_elements_list = r.html.find(".valid")

    for law_link_element in laws_link_elements_list:
        law_url = next(iter(law_link_element.absolute_links))
        await retrieve_law_and_abstract(law_url)


async def retrieve_english_laws_and_abstracts_from_pagination_pages(pagination_url_list):
    english_laws_and_abstracts_path = os.path.join(
        os.path.curdir, "english_laws_with_abstracts", "df.csv")

    if not os.path.exists(english_laws_and_abstracts_path):
        columns = ['law_url', 'abstract_url', 'is_standardized']
        df = pd.DataFrame(columns=columns)
        df.to_csv(english_laws_and_abstracts_path, index=False)

    for pagination_url in pagination_url_list:
        await retrieve_page_from_pagination(pagination_url)
