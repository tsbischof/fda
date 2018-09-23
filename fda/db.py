import os
import io
import urllib.request
import zipfile

import pandas

import fda

def get_510k_db(root_dir=os.path.join(fda.root_db_dir, "510k")):
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
        
    db_urls = [
        "http://www.accessdata.fda.gov/premarket/ftparea/pmnlstmn.zip",
        "http://www.accessdata.fda.gov/premarket/ftparea/pmn96cur.zip",
        "http://www.accessdata.fda.gov/premarket/ftparea/pmn9195.zip",
        "http://www.accessdata.fda.gov/premarket/ftparea/pmn8690.zip",
        "http://www.accessdata.fda.gov/premarket/ftparea/pmn8185.zip",
        "http://www.accessdata.fda.gov/premarket/ftparea/pmn7680.zip"
    ]
    
    db = pandas.concat(map(lambda url: load_510k_db(url, root_dir), db_urls))
    db = db.drop_duplicates().reset_index().drop("index", axis=1)
    return(db)

def load_510k_db(url, root_dir):
    db_filename = os.path.join(root_dir, os.path.basename(url))

    if not os.path.exists(db_filename):
        urllib.request.urlretrieve(url, db_filename)
    
    frames = list()
    with zipfile.ZipFile(db_filename) as db:
        for filename in db.filelist:
            raw = db.read(filename).decode("iso8859_2")
            data = pandas.read_csv(io.StringIO(raw), delimiter="|")
            frames.append(data)
            
    return(pandas.concat(frames))
    
