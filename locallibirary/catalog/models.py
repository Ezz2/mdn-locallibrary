from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

import uuid
from datetime import date

# # Create your models here.
# class MyModelname(models.Model):
    
#     """A typical class defining a model, derived from the Model class."""
    
#     # Fields
#     my_field_name = models.CharField(max_length=20, help_text="Enter field documentation")
#     # ...
    
#     # Metadata
#     class Meta:
#         ordering = ['-my_field_name']
#         verbose_name = "My Model Name"
    
#     # Methods
#     def get_absolute_url(self):
        
#         """Returns the URL to access a particular instance of MyModelName."""
#         return reverse('models-detail-view', args=[str(self.id)])
    
#     def __str__(self):
        
#         return self.my_field_name

# # Create a new record using the model's constructor.
# record = MyModelname(my_field_name="Instance #1")

# # Save the object into the database.
# record.save()

# # Change record by modifying the fields, then calling save().
# record.my_field_name = "New Instance Name"
# record.save()


class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction)")
    
    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Language(models.Model):
    
    all_lang = (
        ("English", "English"),
        ("France", "France"),
        ("German", "Germany"),
    )
    
    name = models.CharField(max_length=200, help_text="Enter a book language", choices=all_lang, default="English")
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author is a string rather than an object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    
    isbn = models.CharField("ISBN", max_length=13, unique=True, 
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    
    display_genre.short_description = "Genre"

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    # imprint = models.CharField(max_length=200, default="im")
    due_back  = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    
    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability"
    )
    
    class Meta:
        ordering = ['due_back']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.book.title} ({self.id})'
    
    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(date.today() > self.due_back)
    
    class Meta:
        permissions = (("can_mark_returned", "Set book as returned"),) 

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.first_name.capitalize()}, {self.last_name}'
