## Copyright (c) 2006 Nathan R. Yergler, Creative Commons

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the "Software"),
## to deal in the Software without restriction, including without limitation
## the rights to use, copy, modify, merge, publish, distribute, sublicense,
## and/or sell copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## DEALINGS IN THE SOFTWARE.

import os
import cherrypy
import simplejson
import rdfadict

def jsondefault(func):
    """Decorator which catches any exceptions thrown by [func] and returns
    an empty JSON mapping ('{}') if [func] does not complete successfully.
    """
    
    def catch_wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except:
            return simplejson.dumps({})

    return catch_wrapper

class DeedScraper(object):

    @cherrypy.expose
    @jsondefault
    def scrape(self, url):

        # parse the RDFa from the document
        parser = rdfadict.RdfaParser() 
        triples = parser.parseurl(url)

        # extract the bits we care about
        license_url = triples.setdefault(url, {}).get(
            'http://www.w3.org/1999/xhtml#license', triples[url].get(
            'http://web.resource.org/cc/license', [''])
                                       )[0]

        attr_name = triples[url].get(
            'http://web.resource.org/cc/attributionName', [''])[0]
        attr_url =  triples[url].get(
            'http://web.resource.org/cc/attributionURL', [''])[0]
        more_perms = triples[url].get(
            'http://web.resource.org/cc/morePermissions', [''])[0]
        
        # assemble a dictionary to serialize
        attribution_info = {'licenseUrl':license_url,
                            'attributionName':attr_name,
                            'attributionUrl':attr_url,
                            'morePermissions':more_perms
                            }

        # return the data encoded as JSON
        return simplejson.dumps(attribution_info)
    
def serve(host='localhost', port=8082):

    cherrypy.tree.mount(DeedScraper())

    cherrypy.server.socket_host = host
    cherrypy.server.socket_port = port
    cherrypy.server.quickstart()
    cherrypy.engine.start()

if __name__ == '__main__':
    serve()