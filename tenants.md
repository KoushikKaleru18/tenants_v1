
## Django Tenants

After baseic single tenant Project/app creation:

- Install Django Tenants Pkg

```sh
$ pip3 install django-tenants
```

- Add `django_tenants` in settings.py - INSTALLED_APPS at the very 1st line

``` python
INSTALLED_APPS = [
    'django_tenants',
    ...
]
```

- Do the below, create SHARED_APPS, TENANT_APPS and append them into INSTALLED_APPS

``` python
# shared across all tenants
SHARED_APPS = [
    'django_tenants',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'django_htmx',
    'django.contrib.sites',
    'allauth',
    'allauth.account',

    # My apps
    'a_home',
    'a_users',
    
    # Third party
    'django_browser_reload',
]

# only used for tenant specific
TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',

    # My apps
    'a_home',
    'a_users',
]


INSTALLED_APPS = SHARED_APPS + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]
```


- Add Django Tenant Middleware

``` python
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    	...
]
```


- Change DATABASES - ENGINE to 
```
'ENGINE': 'django_tenants.postgresql_backend',
```

and add DATABASE_ROUTERS below DATABASES

``` python
DATABASE_ROUTERS = [
    'django_tenants.routers.TenantSyncRouter'
]
```


### Tenant Manager App

- Create a Tenant Manager app
```
$ python3 manage.py startapp a_tenant_manager
```

#### add this app in SHARED_APPS list, below django_tenants


- add TENANT_MODEL and TENANT_DOMAIN_MODEL in `settings.py`
``` python
TENANT_MODEL = "a_tenant_manager.Tenant"
TENANT_DOMAIN_MODEL = "a_tenant_manager.Domain"
```
and we need to create the above two mentioned models in `a_tenant_manager` app.

- open `a_tenant_manager.models.py`, add

``` python
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

# Create your models here.

class Tenant(TenantMixin):
	name = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True)


class Domain(DomainMixin):
	pass
```


- Migrate `a_tenant_manager` models

```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

after this, the migration log will look different
``` log
[standard:public] === Starting migration
[standard:public] Operations to perform:
[standard:public]   Apply all migrations: a_home, a_tenant_manager, a_users, account, admin, auth, contenttypes, sessions, sites
[standard:public] Running migrations:
[standard:public]   Applying a_tenant_manager.0001_initial...
[standard:public]  OK
```

Finally add a setting in `settings.py` under TENANT_DOMAIN_MODEL

``` python
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True
```
this is to tell Django that, if no tenant is fount, it should display Public app



### Create Tenants

- To create a tenant named - `coffeeshop`, use 

```
$ python3 manage.py create_tenant
schema name: coffeeshop
name: Coffee Shop
domain: coffeeshop.localhost
is primary (leave blank to use 'True'):
```

- To create a superuser for a specific tenant
```
$ python3 manage.py create_tenant_superuser
Enter Tenant Schema ('?' to list schemas): ?
0) coffeeshop - coffeeshop.localhost
Enter Tenant Schema ('?' to list schemas): coffeeshop
Username (leave blank to use 'rick'): rick_coffeeshop
Email address: rick_coffeeshop@gmail.com
Password: 
Password (again): 
Superuser created successfully.
```

- now u can navigate to url
http://coffeeshop.localhost:8000/
http://coffeeshop.localhost:8000/admin/
which opens up the coffeeshop tenant app


### Create a Tenant Admin site to manage all the Tenant 

(a_tenant_manager/admin.py)
``` python
from django.contrib import admin
from .models import Tenant, Domain


# Register your models here.


class TenantAdminSite(admin.AdminSite):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.register(Tenant)
		self.register(Domain)


tenant_admin_site = TenantAdminSite(name="tenant_admin_site")
```


- Create Public Urls (copy a_core/urls.py to a_core/urls_public.py)

and add urlpatterns

``` python

from a_tenant_manager.admin import tenant_admin_site

urlpatterns = [
	path('admin_tenants/', tenant_admin_site.urls),
	...
]
```

and add these urls in `settings.py` under ROOT_URL_CONF

``` python
PUBLIC_SCHEMA_URLCONF = 'a_core.urls_public'
```




### Add colors to Navbar based on tenants

- Install django-colorfield

and add it in SHARED_APPS

```
python3 manage.py makemigrations

python3 manage.py migrate_schemas
```

`migrate_schemas` command for migrating to all schemas.. it also have other options which we can use


- to migrate only SHARED_APPS 
 python3 manage.py migrate_schemas --shared

 - to migrate only TENANT_APPS
 python3 manage.py migrate_schemas --tenant

 - to migrate to only a specific tenant
 python3 manage.py migrate_schemas --schema=<tenant_name>

 - to migrate all schemas migrations in parallel
 python3 manage.py migrate_schemas --executor=parallel


now we need to change the header color based on the tenant

create a `templatetags` folder in a_home, and create 2 files
1. __init__.py
2. header.py
``` python
from django.template import Library
from a_home.models import SiteSetting

register = Library() 

@register.inclusion_tag('includes/header.html') 
def header_view(request):
    branding = SiteSetting.objects.first()
    if branding:
        color = branding.color
    else:
        color = None
 
    context = {
        'request' : request,
        'color' : color,
    }
    return context
```


and now replace where u r including header.html in base.html

change
    `{% include 'includes/header.html' %}`
    to
    ```
    {% load header %}
    {% header_view request %}
    ```


### To add logo for tenants

in SiteSetting model add

```
logo = models.ImageField(upload_to="logo/", null=True, blank=True)
```




### Upload the files based on tenants - to its respective tenants 

add Django Tenant Storage configuration which comes directly from Django Tenants package

in `settings.py` :

add this below MEDIA_ROOT

``` python
STORAGES = {
    "default": {
        "BACKEND": "django_tenants.files.storage.TenantFileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

This works fine with new projects, but if u already have users, and want to map the already existing media with public domain, do:

create `storage.py` in `a_home` app

``` python
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django_tenants.files.storage import TenantFileSystemStorage


class CustomSchemaStorage:
    def _get_storage_backend(self):
        schema_name = connection.schema_name

        if schema_name == 'public':
            return FileSystemStorage()
        else:
            return TenantFileSystemStorage()


    def save(self, name, content, max_length=None):
        storage_backend = self._get_storage_backend()
        return storage_backend.save(name, content, max_length)

    def url(self, name):
        storage_backend = self._get_storage_backend()
        return storage_backend.url(name)
    
    def generate_filename(self, name):
        storage_backend = self._get_storage_backend()
        return storage_backend.generate_filename(name)

```


after creating this, change 

``` python
STORAGES = {
    "default": {
        "BACKEND": "django_tenants.files.storage.TenantFileSystemStorage",
    },
    ...
}
```
to 

``` python
STORAGES = {
    "default": {
        "BACKEND": "a_home.storage.CustomSchemaStorage",
    },
    ...
}
```


and to move all the tenants' media into a tenant folder, add

``` python
MULTITENANT_RELATIVE_MEDIA_ROOT = "tenants/%s"
```