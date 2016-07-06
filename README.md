
=====
Badgesfab
=====

badgesfab is a simple Django app to create and attribute Badges to your
users for theirs engagements. This app override a lot of Taggit Model and 
Manager Classes.

In this app, we handle for you the MultiTagManager support to avoid
conflict if other TagManager were declared.

 

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "badgesfab" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django.contrib.sites',
        'actstream',
        'badgesfab',
        'django_filters',
        'crispy_forms',
        'rest_framework',
        'fakesketchfab',
        'taggit',
        'djmoney',
        'badgesfab',
    ]

2. Include the badgesfab URLconf in your project urls.py like this::

    url(r'^badges/', include('badgesfab.urls')),
    
Query URL http://127.0.0.1:8000/badges/list/ to get all URL

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


Builtin rule of attribution:

How to read this rule:

If an <Actor> <Verb> 

Actor: User
Verb: "reached 1k views"
Target: "Model3d"

Actor: User
Verb: "uploaded more than 5"
Target: "Model3d"

Actor: User
Verb: "exists for more than 1 year"
