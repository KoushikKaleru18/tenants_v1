from django.core.management.base import BaseCommand
# from django_tenants.utils import get_tenant_model, get_domain_model
from a_tenant_manager.models import Tenant, Domain

class Command(BaseCommand):
    help = "Create initial tenants"

    def handle(self, *args, **kwargs):
        # Tenant = get_tenant_model()
        # Domain = get_domain_model()

        schema_name = "school"
        tenant_name = "School Tenant"
        domain_name = "school.tenants-v1.onrender.com"  # change this

        # Avoid duplicate tenants
        if Tenant.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(self.style.WARNING("Tenant already exists. Skipping."))
            return

        tenant = Tenant.objects.create(
            schema_name=schema_name,
            name=tenant_name,
        )

        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True,
        )

        self.stdout.write(self.style.SUCCESS("Tenant created successfully"))
