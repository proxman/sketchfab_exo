
=====
Badgesfab
=====

badgesfab is a simple Django app to create and attribute Badges to your
users for theirs engagements. This app override a lot of Taggit Model and 
Manager Classes.

In this app, we override TagManager [to avoid conflict ](http://django-taggit.readthedocs.io/en/latest/changelog.html?highlight=multiple#id28) if other TagManager 
were declared.


Quick start
-----------

1. Add "badgesfab" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django.contrib.sites',
        'actstream', # Optional -> Future support
        'badgesfab',
        'django_filters', # Filtering support for rest_framework
        'crispy_forms', # Improved HTML display for filtering
        'rest_framework',
        'fakesketchfab', # Fake sketchfab app
        'taggit', # required for Badgesfab
        'djmoney', # 
        'badgesfab',
    ]

2. Include the badgesfab URLconf in your project urls.py like this::

    url(r'^badges/', include('badgesfab.urls')),
    
Query URL http://127.0.0.1:8000/badges/list/ to get all URL
Query URL http://127.0.0.1:8000/explore/userlist/ to get users badge

### TODO

- [ ] create HyperlinkedModelSerializer to badge instead of badge ID.
- [ ] import data.sql rule a install
- [ ] Make reusable app :)
- [x] ...

Then run:
3.  `python manage.py check`
4.  `python manage.py migrate` to create the badgesfab models.
5.  `python manage.py makemigrations badgesfab`
6.  `python manage.py makemigrations fakesketchfab`
7.  `python manage.py migrate`
8.  `python manage.py createsuperuser`


9. Start the development server and visit http://127.0.0.1:8000/admin/
   to create badges and define the rules of attribution
   (you'll need the Admin app enabled).

there is a data.sql file with built in rule

