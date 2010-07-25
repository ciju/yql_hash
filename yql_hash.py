import os, re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from plogging import log
from decorators import returns_json, allowed_for
from models import IndexedYQL, Tags

__author__ = "ciju.ch3rian@gmail.com (ciju cherian)"

class YQL_hash(webapp.RequestHandler):
    def _get_fn_doc_hash(self, f, s, fname):
        return {'fun': fname, 'doc':getattr(YQL_hash, s+f).__doc__}

    def _methods_starting_with(self, s):
        ms = [re.search('^'+s+'(.*)', m) for m in
              dir(YQL_hash)]
        return [r.group(1) for r in filter(None, ms)] 

    def _gen_doc(self, typ):
        bfix = typ+'_'
        pfix = 'rpc_'+bfix
        return [self._get_fn_doc_hash(f, pfix, bfix+f) for f in
                self._methods_starting_with(pfix)]
        
    @returns_json
    def _process_request(self, suffix='rpc_'):
        args = {}
        for arg in self.request.arguments():
            args[str(arg)] = str(self.request.get(arg))

        action, resource = None, None
        if 'action' in args:
            action = args['action']
            del args['action']

        func = getattr(self, suffix + action, None)
        if not func:
            res = { 'status': 'not_found' }
        elif resource:
            res = func(resource, **args)
        else:
            res = func(**args)

        if 'status' not in res:
            res = { 'status': 'ok', 'result': res }

        { 'not_found' : lambda: self.error(404)
          , 'error'     : lambda: self.error(500)
          }.get(res['status'], lambda: 'do nothing')()

        return res

    def get(self):
        return self._process_request()

    def post(self):
        return self._process_request()

    def rpc_get_rpc_method_list(self):
        """
        Lists all the methods available to be called in the api.
        @returns array with function name and there respective
                 documentation.
        """
        methods = dict([[m+'s', self._gen_doc(m)] for m in
                        ['get', 'post']]) 
        return { 'methods' : methods }

    @allowed_for('user')
    def rpc_post_index(self, index, yql_query, tag, fn=None, desc=''):
        """
        Creates an index in the backend. In other words search
        string to query association. Ex: the search string could
        be 'cute cats' with the yql query.
        
        'select * from search.images where query="cute cats" and mimetype like "%jpeg%"'
        
        @argument index The string user would search with. ex: 'cute cats'
        @argument yql_query The query string. Like the one above.
        @argument tag The tag you might want to associate with the string.
                      Ex: '/animals/cats'.
        @argument desc Any details you might want to add (not used anywhere)

        @returns id Essentially of no use, till now.
        
        @note One more parameter might be added to this.
        """

        y = IndexedYQL.create(index, yql_query, tag, fn, desc)
        if not y:
            return {
                'status': 'error',
                'message': 'the index already exists'
                }
        return {'id': str(y.key().id())}

    @allowed_for('user')
    def rpc_get_index(self, index):
        """
        Returns the result for the search string. In the backend,
        the yql query is executed and result formater and
        returned.

        @argument index The search string.
        
        @result The result of yql search.
        """
        res = IndexedYQL.get_index_result(index)
        if not res:
            return {}
        return res

    @allowed_for('user')
    def rpc_get_tag_list(self, tag=''):
        """
        @returns The Hierarchy of tags.
        """
        return Tags.get_hierarchy(tag)

    @allowed_for('user')
    def rpc_get_indexes_for_tag(self, tag):
        """
        Get search strings for the specified tag.

        @argument tag
        @returns 
        """
        indexes = Tags.get_indexes(tag)
        if not indexes:
            return {}
        return indexes


class MainPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        # self.response.headers["Cache-Control"] = "private; max-age=3153600"
        # template_values['events'][1]['time'] = int(time.time()*1000)
        self.response.out.write(open(path, 'r').read())
        
    

application = webapp.WSGIApplication(
    [
        ('/', MainPage),
        ('/api', YQL_hash)
        ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
