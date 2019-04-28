import os
from bs4 import BeautifulSoup
from whoosh import scoring
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import open_dir, create_in
from whoosh.qparser import MultifieldParser, OrGroup

def create_index(index_dir_name):
    '''
    Takes a directory of files and indexes them in a directory so that they may be searched through.


    Args:
        index_dir_name (str) = name of directory for index to be stored in

    '''

    #analyser object for pre-processing search terms 
    stem_analyzer = StemmingAnalyzer()

    #create search schema
    schema = Schema(title=TEXT(analyzer = stem_analyzer, stored=True),path=ID(stored=True),
              content=TEXT(analyzer = stem_analyzer, stored=True),textdata=TEXT(stored=True))

    #if path to index does not exist, create it 
    if not os.path.exists(index_dir_name):
        os.mkdir(index_dir_name)
 
    # Creating a index writer to add document as per schema
    ix = create_in(index_dir_name,schema)
    writer = ix.writer()

    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/faqs/"
 
    #parses every file in FAQs folder and extracts question and answer text data
    filepaths = [os.path.join(dir_path,i) for i in os.listdir(dir_path)]
    for path in filepaths:
        html = BeautifulSoup(open(path,'r'), "lxml")
        #parse question text
        question = html.find("div", {"id" : "question"}).getText()
        #parse answer text
        answer = html.find("div", {"id" : "answer"}).getText()
        formatted_answer = answer.replace(u'Â\xa0', u' ').replace(u".", u". ")
        writer.add_document(title=question, path=path,
          content=formatted_answer,textdata=formatted_answer)
    writer.commit()
    

def conduct_search(query_str, index_dir_name, results_no = 3):
    '''
    Conducts search over indexed documents using a user-provided query.


    Args:
        query_str (string): The query used for the search
        index_dir_name (string): The name of the directory containing the index
        results_no (int, optional): The top n results returned to the user. Defaults to 3.


    Returns:
        results_list: A ranked list of 3 tuples containing highest scoring question and answer text
        
    '''

    #open the index directory
    ix = open_dir(index_dir_name)

    #conduct index search
    with ix.searcher(weighting=scoring.BM25F()) as searcher:
        query = MultifieldParser(["title", "content"], ix.schema, group=OrGroup).parse(query_str)
        results = searcher.search(query,limit=results_no,terms=True)
        if results_no < len(results):
            results_list = [(results[num]["title"], results[num]["content"]) for num in range(results_no)]
        else:
            results_list = [(results[num]["title"], results[num]["content"]) for num in range(len(results))]
        return results_list

