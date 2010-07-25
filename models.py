import os
from google.appengine.ext import db

from plogging import log
import utils

import lib.yql as yql

__author__ = "ciju.ch3rian@gmail.com (ciju cherian)"

class Tags(db.Model):
    tag = db.StringProperty(indexed=True, required=True)

    @classmethod
    def get_indexes(cls, tag):
        tag = Tags.gql('where tag=:t', t=tag).fetch(1)
        if not tag:
            return False
        tag = tag[0]

        indexes = IndexedYQL.gql('where tag_ref=:t', t=tag).fetch(1000)
        return [i.index for i in indexes]

    @classmethod
    def get_hierarchy(cls, tag=''):
        hier = {}
        def update_hier(tag):
            lh = hier
            entries = tag.split('/')
            for e in entries:
                if not e in lh:
                    lh[e] = {}
                lh = lh[e]

        for t in Tags.all():
            update_hier( utils.slashify(t.tag) )

        return hier

    

class IndexedYQL(db.Model):
    index = db.StringProperty(indexed=True, required=True)
    tag_ref = db.ReferenceProperty(Tags)
    yql_query = db.StringProperty(indexed=False, required=True)
    fn = db.StringProperty(indexed=False, required=False)
    desc = db.StringProperty(indexed=False, required=False)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls, index, q, tag,fn=None,  desc=''):
        y = IndexedYQL.gql('where index = :i',
                           i=index).fetch(1)
        if y:
            return False

        y = IndexedYQL(index=index, yql_query=q, fn=fn, desc=desc)
        y.tag_ref = Tags(tag=tag).put()
        y.put()
        return y

    @classmethod
    def get_by_index(cls, raw_index):
        idx = cls.convert_raw_to_index(raw_index)
        y = IndexedYQL.gql('where index = :i', i=idx).fetch(1)
        if not y:
            return False
        y = y[0]
        return y

    @classmethod
    def get_index_result(cls, raw_index):
        obj = cls.get_by_index(raw_index)
        if not obj:
            return False

        y = yql.Public()
        res = y.execute(obj.yql_query)
        if obj.fn:
            res = eval(obj.fn)  # todo: make it safer.
        return res
        

    @classmethod
    def convert_raw_to_index(cls, idx):
        
        return idx
    
