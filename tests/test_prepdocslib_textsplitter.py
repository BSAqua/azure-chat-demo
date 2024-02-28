import shutil
from pathlib import Path

import pytest
import tiktoken

from scripts.prepdocslib.listfilestrategy import LocalListFileStrategy
from scripts.prepdocslib.page import Page
from scripts.prepdocslib.pdfparser import LocalPdfParser
from scripts.prepdocslib.searchmanager import Section
from scripts.prepdocslib.textsplitter import SentenceTextSplitter, SimpleTextSplitter


def test_sentencetextsplitter_split_empty_pages():
    t = SentenceTextSplitter(False, True)

    assert list(t.split_pages([])) == []


def test_sentencetextsplitter_split_small_pages():
    t = SentenceTextSplitter(has_image_embeddings=False, verbose=True)

    split_pages = list(t.split_pages(pages=[Page(page_num=0, offset=0, text="Not a large page")]))
    assert len(split_pages) == 1
    assert split_pages[0].page_num == 0
    assert split_pages[0].text == "Not a large page"


@pytest.mark.asyncio
async def test_sentencetextsplitter_list_parse_and_split(tmp_path):
    text_splitter = SentenceTextSplitter(False, True)
    pdf_parser = LocalPdfParser()
    for pdf in Path("data").glob("*.pdf"):
        shutil.copy(str(pdf.absolute()), tmp_path)

    list_file_strategy = LocalListFileStrategy(path_pattern=str(tmp_path / "*"), verbose=True)
    files = list_file_strategy.list()
    processed = 0
    async for file in files:
        pages = [page async for page in pdf_parser.parse(content=file.content)]
        assert pages
        sections = [
            Section(split_page, content=file, category="test category")
            for split_page in text_splitter.split_pages(pages)
        ]
        assert sections
        processed += 1
    assert processed > 1


def test_simpletextsplitter_split_empty_pages():
    t = SimpleTextSplitter(True)

    assert list(t.split_pages([])) == []


def test_simpletextsplitter_split_small_pages():
    t = SimpleTextSplitter(verbose=True)

    split_pages = list(t.split_pages(pages=[Page(page_num=0, offset=0, text='{"test": "Not a large page"}')]))
    assert len(split_pages) == 1
    assert split_pages[0].page_num == 0
    assert split_pages[0].text == '{"test": "Not a large page"}'


def test_sentencetextsplitter_split_pages():
    max_object_length = 10
    t = SimpleTextSplitter(max_object_length=max_object_length, verbose=True)

    split_pages = list(t.split_pages(pages=[Page(page_num=0, offset=0, text='{"test": "Not a large page"}')]))
    assert len(split_pages) == 3
    assert split_pages[0].page_num == 0
    assert split_pages[0].text == '{"test": "'
    assert len(split_pages[0].text) <= max_object_length
    assert split_pages[1].page_num == 1
    assert split_pages[1].text == "Not a larg"
    assert len(split_pages[1].text) <= max_object_length
    assert split_pages[2].page_num == 2
    assert split_pages[2].text == 'e page"}'
    assert len(split_pages[2].text) <= max_object_length


def pytest_generate_tests(metafunc):
    """Parametrize the test_doc fixture with all the pdf files in the test-data directory."""
    if "test_doc" in metafunc.fixturenames:
            metafunc.parametrize("test_doc", [pdf for pdf in Path("tests", "test-data").glob("*.pdf")])


@pytest.mark.asyncio
async def test_sentencetextsplitter_multilang(test_doc, tmp_path):
    text_splitter = SentenceTextSplitter(False, True)
    cl100k = tiktoken.get_encoding("cl100k_base")
    pdf_parser = LocalPdfParser()
    
    shutil.copy(str(test_doc.absolute()), tmp_path)

    list_file_strategy = LocalListFileStrategy(path_pattern=str(tmp_path / "*"), verbose=True)
    files = list_file_strategy.list()
    processed = 0
    async for file in files:
        pages = [page async for page in pdf_parser.parse(content=file.content)]
        assert pages
        sections = [
            Section(split_page, content=file, category="test category")
            for split_page in text_splitter.split_pages(pages)
        ]
        assert sections
        processed += 1

        # Verify the size of the sections
        token_lengths = []
        for section in sections:
            assert len(section.split_page.text) <= (text_splitter.max_section_length * 1.2)
            # Verify the number of tokens is below 500
            token_lengths.append(len(cl100k.encode(section.split_page.text)))
        # verify that none of the numbers in token_lengths are above 500
        assert all([x <= 500 for x in token_lengths]), token_lengths
    assert processed >= 1
