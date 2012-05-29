from django.shortcuts import render
from pytm.pytm import Api
import json
from GChartWrapper import *
from models import Categories
import cPickle as pickle
from datetime import timedelta

class TradeMe(object):
    def __init__(self):
        self.tm = Api()

    def listings_per_category(self, category_number):
        listings = json.loads(self.tm.search({"category": category_number}))
        return listings["TotalCount"]

    def subcategory_listings(self, cat):
        data = {}
        if cat["Subcategories"] is not None:
            for sub_cat in cat["Subcategories"]:
                data[sub_cat["Name"]] = self.listings_per_category(sub_cat["Number"])
        return data

    def load_categories(self):
        site_updated = self.tm.categories_updated()

        c = Categories.objects.get(id=1)
        cache_updated = c.last_updated
        if (site_updated - cache_updated) <= timedelta(seconds = 0):
            pcat = c.categories
            cat = pickle.loads(pcat)
        else:
            cat = json.loads(self.tm.categories())
            pcat = pickle.dumps(cat)
            c1 = Categories(id=1, categories=pcat, last_updated=site_updated)
            c1.save()

        return cat

    def get_subcategory_listings(self):
        cat = self.load_categories()
        return self.subcategory_listings(cat)

def home(request):
    t = TradeMe()
    categories, num_listings = zip(*t.get_subcategory_listings().iteritems())
    #G = GChart('pie', num_listings).title('Categories')
    G = VerticalBarGroup(num_listings)
    G.color('4d89f9','c6d9fd')
    G.size(600,371)
    G.label(["Categories","Listings"])
    G.legend(",".join('"%s"' % i for i in categories))

    return render(request, 'home.html', {'chart': G.img()})