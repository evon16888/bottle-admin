# coding: utf-8
import pytest
from bottle_application import Product
from bottle_admin.auth.models import User
from bottle_admin.sites import AdminSite, AlreadyRegistered, NotRegistered


@pytest.fixture(scope="function")
def site(request):
    site = AdminSite()
    return site


class TestAdminSite(object):
    def test_register(self, site):
        assert len(site._registry) == 0

        site.register(Product)
        assert len(site._registry) == 1

        with pytest.raises(AlreadyRegistered):
            site.register(User)
            site.register(Product)

    def test_get_model_class(self, site):
        with pytest.raises(NotRegistered):
            site.get_model_class('user')

        with pytest.raises(NotRegistered):
            site.get_model_class('product')

        site.register(User)
        assert site.get_model_class('user') == User

        site.register(Product)
        assert site.get_model_class('product') == Product

    def assert_model_meta(self, meta, model, columns):
        model_name = model.__name__.lower()
        assert meta['name'] == model_name
        assert set(meta['columns']) == columns
        assert meta['add_url'] == '{0}/{1}/add'.format(AdminSite.url_prefix, model_name)
        assert meta['list_url'] == '{0}/{1}'.format(AdminSite.url_prefix, model_name)
        edit_url = '{0}/{1}/edit'.format(AdminSite.url_prefix, model_name)
        assert meta['edit_url'] == edit_url
        delete_url = '{0}/{1}/delete'.format(AdminSite.url_prefix, model_name)
        assert meta['delete_url'] == delete_url

    def test_get_model_meta_list(self, site):
        assert site.get_model_meta_list() == []

        site.register(User)
        metas = site.get_model_meta_list()
        columns = set(('username', 'fullname', 'hash', 'creation_date',
                       'role', 'email_addr', 'desc', 'last_login'))
        self.assert_model_meta(metas[0], User, columns)

        site._registry = []
        site.register(Product)
        metas = site.get_model_meta_list()
        columns = set(('name', 'description', 'price'))
        self.assert_model_meta(metas[0], Product, columns)

    def test_get_model_meta(self, site):
        with pytest.raises(NotRegistered):
            site.get_model_meta('user')

        site.register(User)
        meta = site.get_model_meta('user')
        columns = set(('username', 'fullname', 'hash', 'creation_date',
                       'role', 'email_addr', 'desc', 'last_login'))
        self.assert_model_meta(meta, User, columns)

        site.register(Product)
        meta = site.get_model_meta('product')
        columns = set(('name', 'description', 'price'))
        self.assert_model_meta(meta, Product, columns)
