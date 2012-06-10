from django.shortcuts import render
from pytm.pytm import Api
import json
from GChartWrapper import *
from models import Categories
import cPickle as pickle
import datetime

# for debugging probably not needed usually
from pprint import pprint
import sys

class TradeMe(object):
    def __init__(self):
        self.tm = Api()

    def subcategory_listings(self, cat):
        data = {}
        #try:
        if "Subcategories" in cat:
            if cat["Subcategories"] is not None:
                for sub_cat in cat["Subcategories"]:
                    print sub_cat["Number"]
                    j1 = self.load_categories(sub_cat["Number"])
                    if j1 is not None:
                        if "Subcategories" in j1:
                            if j1["Subcategories"] is not None:
                                for sb in j1["Subcategories"]:
                                    if "Count" in sb:
                                        data[sb["Name"]] = sb["Count"]
                                    else:
                                        data[sb["Name"]] = 0
        #except:
        #    print "Unexpected error:", sys.exc_info()[0]
        #    data = None
        pprint(data)
        return data

    def load_new_categories(self, site_updated, number=None):
        print "Loading a new category listing"
        try:
            jcat = self.tm.categories(category=number, with_counts="true")
            cat = json.loads(jcat)
            pcat = pickle.dumps(cat)
            c = Categories.objects.get(number=number)
            c.last_updated = site_updated
            c.categories=pcat
            c.save()
        except Categories.DoesNotExist as e:
            c = Categories(categories=pcat, last_updated=site_updated,
            name=cat["Name"],number=cat["Number"])
            c.save()
        except:
            print "Couldn't fetch new categories", sys.exc_info()[0], number
            cat = None
        return cat

    def load_categories(self, number=None):
        try:
            if number is None:
                site_updated = self.tm.categories_updated()
                c = Categories.objects.get(id=1)
            else:
                site_updated = datetime.datetime.now() 
                c = Categories.objects.get(number=number)

            cache_updated = c.last_updated
            # Change the seconds to affect the caching
            if (site_updated - cache_updated) <= datetime.timedelta(seconds = 60):
                print "Using cached categories"
                pcat = c.categories
                cat = pickle.loads(pcat)
            else:
                print "Cache is old"
                cat = self.load_new_categories(site_updated, number)
        except Categories.DoesNotExist as e:
            print "Categories does not exist!!!"
            cat = self.load_new_categories(site_updated, number)

        return cat

    def get_subcategory_listings(self):
        cat = self.load_categories()
        if cat is not None:
            return self.subcategory_listings(cat)
        return cat

def home(request):
    t = TradeMe()
    listings = t.get_subcategory_listings()
    if listings is not None:
        categories, num_listings = zip(*listings.iteritems())
        #G = GChart('pie', num_listings).title('Categories')
        G = VerticalBarGroup(num_listings)
        G.color('4d89f9','c6d9fd')
        G.size(600,371)
        G.label(["Categories","Listings"])
        G.legend(",".join('"%s"' % i for i in categories))

        return render(request, 'home.html', {'chart': G.img()})
    return render(request, 'home.html')

