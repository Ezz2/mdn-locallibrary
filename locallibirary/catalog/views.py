from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render

import datetime
from .forms import RenewBookForm
from .models import Book, Genre, BookInstance, Author

class AuthorCreate(LoginRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(LoginRequiredMixin, UpdateView):
    model = Author
    fields = "__all__"

class AuthorDelete(LoginRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    fields = ["title", 'author', 'summary', 'isbn', 'genre', 'language']
    # initial = {'date_of_death': '11/06/2020'}

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    fields = "__all__"

class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')

@permission_required('catalog.can_mark_returned')
@login_required
def index(request):
    """View function for home page of site."""
    
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Number of visits to this view, as counted in the session variable., 0 is a default
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    # Available books (status = 'a')
    num_instances_available  = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_visits': num_visits,
    }
    
    # Render the HTML template index.html with the data in the context variable
    return render(request, "catalog/index.html", context=context)

class BookListView(ListView):
    model = Book
    context_object_name = "book_list"
    # queryset = Book.objects.filter(title__icontains='war')[:5]
    queryset = Book.objects.all()
    template_name = "catalog/book_list.html"
    paginate_by = 2
    
    # Get 5 books containing the title war
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5]
    
    # def get_context_data(self, **kwargs):
        
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
        
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

class BookDetailView(DetailView):
    model = Book
    template_name = "catalog/book_detail.html"

# def book_detail_view(request, primary_key):
#     try:
#         book = Book.objects.get(pk=primary_key)
#     except Book.DoesNotExist:
#         return Http404("Book does not exist")
    
#     return render(request, "book_detail.html", context={"book": book})

class AuthorListView(ListView):
    model = Author
    context_object_name = "author_list"
    queryset = Author.objects.all()
    template_name = "catalog/author_list.html"

class AuthorDetailView(DetailView):
    model = Author
    template_name = "catalog/author_detail.html"

class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    context_object_name = 'bookinstance_list'
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10
    
    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o").order_by('due_back'))

class BorrowedListView(PermissionRequiredMixin, ListView):
    permission_required = ('catalog.can_mark_returned')
    model = BookInstance
    context_object_name = 'borrowed_list'
    template_name = 'catalog/borrowed_list.html'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required()
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == "POST":
        
        form = RenewBookForm(request.POST)
        
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('borrowed'))
        
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)
