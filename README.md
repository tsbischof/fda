# Tracing predicates from FDA 510k submissions
Medical devices regulated by the FDA fall into various classifications based on risk, and go through separate pathways depending on the level of due diligence required to assess the technology. In rough order of risk, these are the 510(k), De Novo, and PMA processes.

510k approvals are based on the idea of a "predicate" device, where the new device is deemed substantially equivalent to some existing device in the market. This enables the vendor to use existing safety and efficacy data related to the predicate device to justify the approval of the new device, greatly lowering the burden for approval.

Any given device may have several predicate devices, leading back through their own predicate devices, and so on. Here we trace a given device's ancestry through the approval process, until we either arrive at the original device or the end of the documentation (more likely).

As an example, here is the ancestry of a venous catheter ([K081113](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K081113)):
![K081113](https://github.com/tsbischof/fda/examples/K081113.png)

Now, that catheter has since been used in the ancestry for a version of the Da Vinci robotic surgical system ([K173585](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K173585)). It is the little branch off to the left:
![K173585](https://github.com/tsbischof/fda/examples/K173585.png)

## Usage
### Dependencies
* Python 3 (tested for 3.4+)
 * graphviz
 * networkx
 * pandas
 * pdf2image
 * PyPDF2
* tesseract

### Basic usage
The following script searches the FDA website for approval K173585, then traces back through all predicate devices in that approval letter recursively until either there are not predicates found or the documents are not found online:
```
import networkx

import fda

regulatory_graph = networkx.DiGraph()
regulatory_graph.add_node(fda.empty)
fda.populate_predicates(regulatory_graph, fda.FDAApproval("K173585"))
```

## Caveats
The predicate search algorithm is promiscuous, searching for anything that looks like an approval number (e.g. K[0-9]{6}, DEN[0-9]{8}).

Depending on the author of the approval document, sometimes they reference the device name rather than the approval number. This code does not attempt to identify devices by name, only approval number.

Many pdfs are scans of paper documents, leading to the need to OCR for text extraction. This is all performed automatically using tesseract and not sanitized afterward, which will lead to many dead links.

Not all approval orders are published online, which will lead to many dead links.

## Dataset
To obtain all approval documents, run [this script](scripts/pull_all_510k.py).

Email the author if you want a copy of the current documents. This is about 16GB over 151k approvals as of 2018-11-24.

## Author
This script was written by [Thomas Bischof](https://github.com/tsbischof/fda). Feel free to contact him through github regarding code, data, or anything else.
