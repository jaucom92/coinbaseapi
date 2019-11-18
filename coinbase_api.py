class make_coinbase():
    
    """
    PERSONAL COINBASE API.
    INSTRUCTIONS:
        * ADD ENDPOINTS TO THE DOCSTRING TO ADD THEM TO THE obj
        * FUN : obj.ENDPOINTS() -> displays the current endpoints. Each <.*> represents a keyword argument that you HAVE to fill when calling the endpoint.
        * SHCEMA: obj.endpoint(keyword) -> it is build with the url parts left after the domain. TAKE CARE of the <keyword> inside of it.
    """
    
    
    def __init__(self, default_sandbox='REST API', front_marker='<', back_marker='>'):
        
        import re
        import requests
        import json
        import numpy as np
                
        SANDBOX = {
                'website':'https://public.sandbox.pro.coinbase.com',
                'REST API':'https://api-public.sandbox.pro.coinbase.com',
                'Websocket Feed':'wss://ws-feed-public.sandbox.pro.coinbase.com',
                'FIX API':'tcp+ssl://fix-public.sandbox.pro.coinbase.com:4198'
                }
        
        ### SCHEMA /URL/<.*>/ ?QUERY=<parameter> ### <, > = front_marker, back_marker
        ENDPOINTS = """
        GET /products
        GET /products/<product-id>/book
        GET /products/<product-id>/ticker
        GET /products/<product-id>/trades
        GET /products/<product-id>/candles ?granularity=<86400>
        GET /products/<product-id>/stats
        GET /currencies
        GET /time
        """
        
        ### '-' are converted to '_' (they will be keywords and isn't possible to write them with '-')
        ENDPOINTS = re.sub('GET\s+', SANDBOX[default_sandbox], ENDPOINTS)
        for pattern in np.unique(re.findall('/' + front_marker + '[\w-]*'+ back_marker +'|=' + front_marker + '[\w-]*'+ back_marker, ENDPOINTS)):
            ENDPOINTS = re.sub(pattern, re.sub('-', '_', pattern), ENDPOINTS)
            
        self.explain = lambda : print(ENDPOINTS)
        
        ### p = 'matches keywords like /<product-id>/'
        ### qp = 'matches query parameters as ?granularity=<86000>&grani=<86000>' # the thing inside <> is the default parameter
        p = re.compile('[^/]*//.*' + front_marker + '([^/]*)' + back_marker + '/')
        qp = re.compile('\s?[&\?](\w*)=' + front_marker + '(\w*)' + back_marker)
        URL_IDENTIFIER_REGEX = "(?P<url>" + SANDBOX[default_sandbox] + "/(?P<name>[^\n]*))\n"
        
        def process_url(url, **kwargs):
        
            if locals()['kwargs'] != {}:
                for k, v in kwargs.items():
                    if k in url:
                        if url[url.find(k) - 1] in '?&':
                            patt, repl = next(((q+'=<'+p+'>', q+'='+p) for q, p in qp.findall(url) if q == k))
                            url = re.sub(patt, repl, url)                
                        else:
                            url = re.sub(front_marker + k + back_marker, v, url)                
                    else:
                        raise TypeError(f"Keyword '{k}' doesn't exist inside the url, please enter a valid keyword that is inside the following url: {url}")
                        
            for patt, repl in ((q+'=<'+p+'>', q+'='+p) for q, p in qp.findall(url)):
                url = re.sub(patt, repl, url)
            url = re.sub('\s', '', url)
            
            #if re.search('[^/]*//?:', url) is not None:                
            if front_marker in url or back_marker in url:
                raise ValueError(f'There are missing keywords in {url}')
            
            print(url)
            
            try:
                r = requests.get(url)
            except:
                raise
            else:
                if r.status_code == 200:
                    return json.loads(r.content)
                elif r.status_code == 400:
                    raise ValueError(f'Status code is {r.status_code} and message is {r.content} \n {url}.')
                else:
                    raise ValueError(f'Status code is {r.status_code} and url is: {url}. {r.content}')
        
        def create_endpoint(m):
                                                               
            def prepare_attribute(m):
                               
                NAME = '_'.join([w for w in re.split('/|\s', m.group('name')) if front_marker not in w])

                if p.search(m.group('url')) is None and qp.search(m.group('url')) is None:
                    return re.sub('-', '_', NAME), lambda : process_url(m.group('url'))
                else:
                    return re.sub('-', '_', NAME), lambda **kwargs: process_url(m.group('url'), **kwargs)
            
                
            setattr(self, *prepare_attribute(m))                
        
        for m in re.compile(URL_IDENTIFIER_REGEX).finditer(ENDPOINTS):
            create_endpoint(m)
            
        return

coinbase = make_coinbase()
coinbase.products_candles(product_id='ETH-BTC', granularity=60)
