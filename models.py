from django.db import models

class BlobField(models.Field):
    description = "Blob"
    def db_type(self, connection):
        return 'mediumblob'

class Categories(models.Model):
    categories = BlobField()
    last_updated = models.DateTimeField()

    def __unicode__(self):
        return self.categories