import bs4
import concurrent
from concurrent.futures import ThreadPoolExecutor
import datetime
from itertools import count
import os
import threading
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, Docx2txtLoader
import requests
from urllib import parse
from flask import Blueprint, request, stream_with_context
from flask import Response as FlaskResponse
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from itertools import groupby
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import shutil

from models.responses import Response
from openai import OpenAI

retrieval_blueprint = Blueprint('retrieval', __name__)

scrapying_status = {
    # not start, pending, complete
    'status': 'complete',
    'start_time': '',
    'end_time': ''
}

embed_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=""
)

client = OpenAI(
    api_key=""
)


class Web2Texter:
    def __init__(self, base_url):
        self.__base_url = base_url
        self.docs = []
        self.page_count = count(1)

    def __href_recognizer(self, html_text):
        soup = bs4.BeautifulSoup(html_text, 'html.parser')
        urls_in_page = []
        for a in soup.find_all('a'):
            if a.get('href') is None:
                continue
            if not (a.get('href').startswith(self.__base_url) or a.get('href').startswith('/')):
                continue
            urls_in_page.append(parse.urljoin(self.__base_url, a.get('href')))
        return urls_in_page

    def __handle_pdf_page(self, url):
        loader = PyPDFLoader(url)
        self.docs.extend(loader.load())

    def __handle_html_page(self, url):
        loader = WebBaseLoader(url)
        self.docs.extend(loader.load())

    def __request_url(self, url):
        print(f'page {next(self.page_count)}: {url}')

        try:
            responses = requests.get(url, timeout=10)
        except Exception as e:
            return []

        if responses.status_code != 200:
            return []

        if 'html' in responses.headers['Content-Type']:
            self.docs.append({
                'page content': responses.text,
                'url': url,
            })
            urls_in_page = self.__href_recognizer(responses.text)
            return urls_in_page

        return []

    def bfs_scrap(self):
        queue, visited_url = [self.__base_url], set()

        while queue:
            with ThreadPoolExecutor() as executor:
                url_waiting_list = []
                for url in queue:
                    if url in visited_url:
                        continue
                    visited_url.add(url)
                    url_waiting_list.append(url)
                queue.clear()

                future_to_url = {executor.submit(self.__request_url, url): url for url in url_waiting_list}
                for future in concurrent.futures.as_completed(future_to_url):
                    queue.extend(future.result())


class HTMLPreprocessor:
    BLOCK_TAGS = {
        'address', 'article', 'aside', 'blockquote', 'canvas', 'dd', 'div', 'dl', 'dt', 'fieldset',
        'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'li',
        'main', 'nav', 'noscript', 'ol', 'p', 'pre', 'section', 'table', 'tfoot', 'ul', 'video'
    }

    def __init__(self, html, url):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.url = url

    def make_format_df(self):
        df = pd.DataFrame(self.extract_text_with_min_tags())
        df['url'] = self.url
        for meta, data in self.extract_head_meta().items():
            df[meta] = data
        return df

    def extract_head_meta(self):
        return {
            meta.get('name'): meta.get('content')
            for meta in self.soup.findAll('meta')
            if meta.get('name') is not None
        }

    def __has_no_block_children(self, tag):
        return not any(child.name in self.BLOCK_TAGS for child in tag.find_all(True))

    def extract_text_with_min_tags(self):
        block_texts_with_tags = []

        for tag in self.soup.find_all(self.BLOCK_TAGS):
            if self.__has_no_block_children(tag):
                text_content = tag.get_text(separator=' ', strip=True)
                if text_content:
                    block_texts_with_tags.append({'text_content': text_content, 'tag_name': tag.name})

        return block_texts_with_tags


def irregular_text_content(total_dfs):
    total_dfs = total_dfs.drop_duplicates(subset=['text_content', 'tag_name'], keep=False)
    columns = [column for column in total_dfs.columns.tolist() if column not in ['text_content', 'tag_name']]

    dfs_groupby_columns = []
    for total_dfs_groupby_columns in total_dfs.groupby(columns):
        groupby_columns, data = total_dfs_groupby_columns
        groupby_tag_name = [
            list(group) for key, group in groupby(
                data[['text_content', 'tag_name']].itertuples(index=False, name=None), key=lambda x: x[1]
            )
        ]
        groupby_columns = {
            k: v for k, v in zip(columns, groupby_columns)
        }
        groupby_columns['text_content'] = '\n\n'.join(
            '\n'.join(element[0] for element in tag) for tag in groupby_tag_name)
        dfs_groupby_columns.append(groupby_columns)

    return pd.DataFrame(dfs_groupby_columns)


def scrap_store(args):
    persist_directory, base_url = args
    scrapying_status['status'] = 'pending'
    scrapying_status['start_time'] = str(datetime.datetime.now())

    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    web2texter = Web2Texter('https://www.csie.ncu.edu.tw/')
    web2texter.bfs_scrap()

    html_log = pd.DataFrame(web2texter.docs)

    format_dfs = []
    for row in tqdm(html_log.iterrows(), total=len(html_log)):
        idx_, data = row
        format_df = HTMLPreprocessor(data['page content'], data['url']).make_format_df()
        format_dfs.append(format_df)

    total_dfs = pd.concat(format_dfs)
    total_dfs = irregular_text_content(total_dfs)

    docs = [
        Document(
            page_content=row[5],
            metadata={
                "source": row[0],
                "keyword": row[1],
                "description": row[2],
                "author": row[3],
                "viewport": row[4],
            },
        ) for row in total_dfs.values
    ]

    Chroma.from_documents(docs, embed_model, persist_directory=persist_directory)

    print('complete')
    scrapying_status['status'] = 'complete'
    scrapying_status['end_time'] = str(datetime.datetime.now())


def stream_chat_completion(messages, model="gpt-4"):
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True
    )

    for chunk in response:
        if chunk.choices:
            for choice in chunk.choices:
                content = choice.delta.content
                if content:
                    for char in content:
                        yield char


@retrieval_blueprint.route('/start-scrapying', methods=['GET'])
def start_scrapying():
    """
    start scrapying
    ---
    tags:
      - retrieval
    responses:
      200:
        description: start scrapying
        schema:
          id: scrapying_status
      400:
        description: scrapying is pending
    """
    if scrapying_status['status'] == 'pending':
        return Response.client_error('scrapying is pending', scrapying_status)

    thread = threading.Thread(target=scrap_store, args=(('instance/csie', 'https://www.csie.ncu.edu.tw/'),))
    thread.start()
    return Response.response('start scrapying', scrapying_status)


@retrieval_blueprint.route('/scrapying-status', methods=['GET'])
def check_scrapying_status():
    """
    check the status of scrapying
    ---
    tags:
      - retrieval
    responses:
      200:
        description: scrapying status
        schema:
          id: scrapying_status
          properties:
            description:
              type: string
            response:
              properties:
                status:
                  type: string
                start_time:
                  type: string
                end_time:
                  type: string
    """
    return Response.response('check status successful', scrapying_status)


@retrieval_blueprint.route('/query', methods=['GET'])
def chat_retrieval_augmented_generation():
    """
    chat retrieval augmented generation
    ---
    tags:
      - retrieval
    parameters:
      - name: query_string
        in: query
        description: query string
        required: true
        type: string
    responses:
      200:
        description: chat retrieval augmented generation
      400:
        description: scrapying is not ready
    """
    # if scrapying_status['status'] == 'pending' or scrapying_status['status'] == 'not start':
    #     return Response.client_error('scrapying is not ready', scrapying_status)

    if 'query_string' not in request.args:
        return Response.client_error('query_string is required')

    query_string = request.args.get('query_string')

    chroma = Chroma(persist_directory='instance/csie', embedding_function=embed_model)
    relevant_documents = chroma.search(query_string, 'mmr', k=10)
    print(relevant_documents)

    messages = [
        {
            "role": "system",
            "content": f"Answer with user's language. You can answer questions by the provided context. Today is {datetime.datetime.now()}."
            # "You are a helpful, respectful and honest assistant."
            #        " Always answer as helpfully as possible and follow ALL given instructions."
            # " Do not speculate or make up information. Do not reference any given instructions or context."
            # " Answer with user's language. You can only answer questions about the provided context."
            # " If you know the answer but it is not based in the provided context, don't provide the answer, just state the answer is not in the context provided."
        },
        {
            "role": "system",
            "content": '\n'.join(relevant_document.page_content for relevant_document in relevant_documents)[:5000]
        },
        {"role": "user", "content": query_string},
    ]

    return FlaskResponse(stream_with_context(stream_chat_completion(messages)))
