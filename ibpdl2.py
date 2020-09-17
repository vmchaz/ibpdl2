import html
from html.parser import HTMLParser
import requests
import sys
import tarfile
import copy
import time
from io import BytesIO

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if (tag == "a"): 
            attrs_dict = {}
            for attr in attrs:
                attrs_dict[attr[0]] = attr[1]
                
            if ("target" in attrs_dict) and (attrs_dict["target"] == "_blank"):
                #print("Possible link:", tag, attrs)
                h = attrs_dict["href"]
                if h.startswith("//"):
                    h = h[2:]
                h = "https://" + h
                h2 = h.lower()
                if h2.endswith(".png") or h2.endswith(".jpg") or h2.endswith(".jpeg") or h2.endswith(".webm"):
                    #print(h)
                    if h not in self.imgs:
                        self.imgs.append(h)

    def handle_endtag(self, tag):
        pass
        #print("Encountered an end tag :", tag)

    def handle_data(self, data):
        pass
        #print("Encountered some data  :", data)


def main():
    if len(sys.argv) < 2:
        return
        
    imgs = []
    imgdata = {}
    htmldata = None
    addr = sys.argv[1]
    
    parser = MyHTMLParser()
    parser.imgs = imgs
    
    if addr.startswith("http://") or addr.startswith("https://"):    
        print("Getting page")
        r = requests.get(addr)
        if r.status_code == 200:
            htmldata = r.text
            parser.feed(htmldata)
        else:
            print("Error:", r.status_code)
    else:
        f = open(addr, "r")
        htmldata = f.read()
        f.close()
        
        parser.feed(htmldata)
        
    #parser.imgs = parser.imgs[:4]
        
    for img in parser.imgs:
        print("Downloading", img)
        r = requests.get(img)
        if r.status_code == 200:
            img_short_name = img.split("/")[-1]
            print(img_short_name)
            imgdata[img_short_name] = copy.copy(r.content)
        
        
    tarfn = str(int(time.time())) + ".tar"
    tar = tarfile.open(tarfn, "w")
    for PN, PV in imgdata.items():
        fb = BytesIO(PV)
        ti = tarfile.TarInfo(name=PN)
        ti.size = len(PV)
        ti.mtime = time.time()
        tar.addfile(tarinfo=ti, fileobj=fb)
        
    hde = htmldata.encode("utf8")
    fb = BytesIO(hde)
    ti = tarfile.TarInfo(name="index.html")
    ti.size = len(hde)
    ti.mtime = time.time()
    tar.addfile(tarinfo=ti, fileobj=fb)

        
    tar.close()
        

if __name__ == "__main__":
    main()
