import logging
import os
import re
import subprocess
import urllib.request
import warnings

import graphviz
import networkx
import pandas
import pdf2image
import PyPDF2

root_dir = os.path.join(os.path.dirname(__file__), "..", "data")
root_document_dir = os.path.join(root_dir, "documents")
root_db_dir = os.path.join(root_dir, "db")
id_parser = re.compile("(?P<kind>[A-Za-z]{1,3})"
                       "(?P<year>[0-9]{2})"
                       "(?P<index>[0-9]{4})")

class FDAApproval(object):
    def __init__(self, number, kind=None, root_dir=root_document_dir):
        if number == "empty":
            self.number = 0
            self.kind = None
            self.year = None
            self.index = None
            self.id = "K000000"
        elif isinstance(number, str):
            parsed = id_parser.search(number)
            self.kind = parsed.group("kind")
            self.year = parsed.group("year")
            self.index = parsed.group("index")
            self.id = number
            self._root_dir = os.path.join(root_dir, self.kind,
                                          self.year, self.index)
        else:
            raise(ValueError("Unknown approval number: {}".format(number)))
        
        self._predicates = None
        
    def __eq__(self, other):
        return(self.id == other.id)
    
    def __hash__(self):
        return(hash(self.id))
    
    def __repr__(self):
        return("FDAApproval({})".format(str(self)))
               
    def __str__(self):
        return(self.id)
    
    def year(self):
        year_two_digit = int(self.year)
        if year_two_digit > 70:
            prefix = 1900
        else:
            prefix = 2000
            
        return(prefix + year_two_digit)
        
    def retrieve(self):
        if self.index == 0:
            return(None)
        
        dst_filename = self.get_pdf_filename()
        
        urls_to_try = [
            "https://www.accessdata.fda.gov/cdrh_docs/pdf{0}/{1}.pdf".format(
                self.year, str(self)),
            "https://www.accessdata.fda.gov/cdrh_docs/pdf/{0}.pdf".format(
                str(self))
        ]
        
        for url in urls_to_try:
            try:
                urllib.request.urlretrieve(url, dst_filename)
                return
            except urllib.error.HTTPError as err:
                continue
        
        raise(ValueError("could not retrieve document for {}".format(self)))
        
    def get_pdf_filename(self):
        return(os.path.join(self._root_dir, "{}.pdf".format(str(self))))
    
    def get_text_filename(self, page_number):
        return(os.path.join(self._root_dir,
                            "page_{0:03d}.txt".format(page_number)))
    
    def get_pdf(self, force=False):
        if not os.path.exists(self._root_dir):
            os.makedirs(self._root_dir)

        dst_filename = self.get_pdf_filename()

        if force or not os.path.exists(dst_filename):
            logging.info("Downloading document for {}".format(self))
            
            try:
                self.retrieve()
            except ValueError:
                # leave a blank file to note that we tried,
                # in case there really is no file to be foun
                with open(dst_filename, "w") as stream_out:
                    pass

        # we use blank files as placeholders, skip these in output
        if os.path.getsize(dst_filename) > 0:
            pdf = PyPDF2.PdfFileReader(dst_filename)
            return(pdf)            
    
    def transcribe_ocr(self, dpi=600):
        n_pages = PyPDF2.PdfFileReader(self.get_pdf_filename()).getNumPages()
        
        for page_number in range(n_pages):
            page = pdf2image.convert_from_path(self.get_pdf_filename(), dpi, 
                                               first_page=page_number+1,
                                               last_page=page_number+1)[0]
            
            image_filename = os.path.join(
                self._root_dir,
                "page_{0:03d}.png".format(page_number))
            transcription_filename = self.get_text_filename(page_number)
            
            page.save(image_filename, "png")
            subprocess.Popen(["tesseract", image_filename, "stdout"], 
                             stdout=open(transcription_filename, "w")).wait()
            
            os.remove(image_filename)
            
    def get_pages_text(self, force=False):
        pdf = self.get_pdf()
        
        if pdf is None:
            return([])
        
        pages = list()
        
        for page_number in range(pdf.getNumPages()):
            text_filename = self.get_text_filename(page_number)
            if force or not os.path.exists(text_filename):
                page = pdf.getPage(page_number)
                try: 
                    text = page.extractText()
                    with open(text_filename, "w") as stream_out:
                        stream_out.write(text)
                except:
                    logging.info("transcribing {} using OCR".format(self))
                    self.transcribe_ocr()

            if not os.path.exists(text_filename):
                raise(ValueError(
                    "No text transcription available for {}".format(self)))
                
            text = open(text_filename).read()    
            pages.append(text)
            
        return(pages)
    
    def predicates(self):
        def normalize(text):
            return(re.sub("[\s]", "", text))
        
        if self._predicates is None:
            predicates_filename = os.path.join(self._root_dir, "predicates")
            predicates = set()
            
            if os.path.exists(predicates_filename):
                with open(predicates_filename) as stream_in:
                    for line in stream_in:
                        predicates.add(FDAApproval(line))
            else:
                for page in self.get_pages_text():
                    text = normalize(page)
                    parsed = id_parser.findall(text)
                    predicates.update({FDAApproval(number) for
                                       number in parsed})
                        
                if self in predicates:
                    predicates.remove(self)
                        
                with open(predicates_filename, "w") as stream_out:
                    for predicate in predicates:
                        stream_out.write(str(predicate) + "\n")

            self._predicates = predicates
        
        return(self._predicates)

def populate_predicates(graph, seed, max_depth=100):
    graph.add_node(seed) 
    
    leaves = {seed}
    
    depth = 0

    while len(leaves) > 0 and (max_depth is None or depth < max_depth):
        new_leaves = set()
        for device in leaves:  
            try:
                predicates = device.predicates()
            except:
                graph.add_edge(device, empty)
                continue

            if not predicates:
                graph.add_edge(device, empty)

            for predicate in predicates:
                graph.add_edge(device, predicate)
                if graph.out_degree(predicate) == 0:
                    new_leaves.add(predicate)
        
        leaves = new_leaves
        depth += 1

def get_subgraph(graph, node):
    span = networkx.algorithms.bfs_tree(graph, node)
    subgraph = networkx.DiGraph()
    
    for left in span.nodes():
        for right in graph[left]:
            subgraph.add_edge(left, right)
            
    return(subgraph)

def networkx_to_graphviz(graph):
    dst = graphviz.Digraph()
    
    for left, right in graph.edges():
        dst.edge(str(left), str(right))
        
    return(dst)

empty = FDAApproval("empty")

from . import db
