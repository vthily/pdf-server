from django.db import models

from book.models import Book


class Section(models.Model):
    book = models.ForeignKey(Book)
    title = models.TextField()
    has_children = models.BooleanField()

    def __str__(self):
        return "{book} - [{id}] {title}".format(book=self.book, id=self.id, title=self.title)


class Adjacency(models.Model):
    parent = models.ForeignKey(Section, related_name='parent')
    child = models.ForeignKey(Section, related_name='child')

    def get_book(self):
        return self.parent.book

    class Meta:
        unique_together = ('parent', 'child')
