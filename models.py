from django.db import models

class BlobField(models.Field):
    description = "Blob"
    def db_type(self, connection):
        return 'mediumblob'

class Categories(models.Model):
    categories = BlobField()
    last_updated = models.DateTimeField()
    name = models.CharField(max_length=128)
    number = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return self.categories

#class Category(models.Model):
#    number = models.CharField(max_length=32)
#    title = models.TextField()
#
#class Listing(models.Model):
#    category = models.ForeignKey('Category')

