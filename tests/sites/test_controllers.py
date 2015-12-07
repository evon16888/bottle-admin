# coding: utf-8
import pytest
from sqlalchemy.orm import sessionmaker
from webtest import AppError, TestApp

from bottle_application import app, engine, User


@pytest.fixture(scope="function")
def session(request):
    session = sessionmaker(bind=engine)()
    session.query(User).delete()
    return session


@pytest.fixture(scope="function")
def app_test(request):
    app_test = TestApp(app)
    return app_test


def test_add_model_get_controller(session, app_test):
    # TODO: tests with selenium or similar tool
    assert app_test.get('/admin/user/add').status == '200 OK'


def test_add_model_post_controller(session, app_test):
    with pytest.raises(AppError):
        app_test.post('/admin/user/add').status == '200 OK'


def test_delete_model_controller(session, app_test):
    app_test.get('/admin/user/delete/1').mustcontain('not found')

    user1 = User(name='name', fullname='full', password='pass')
    session.add(user1)
    user2 = User(name='name2', fullname='full', password='pass')
    session.add(user2)
    session.commit()

    status = app_test.get('/admin/user/delete/{0}'.format(user1.id)).status
    assert status == '302 Found'
    response = app_test.get('/admin/user/delete/{0}'.format(user1.id))
    response.mustcontain('not found')

    status = app_test.get('/admin/user/delete/{0}'.format(user2.id)).status
    assert status == '302 Found'
    request = app_test.get('/admin/user/delete/{0}'.format(user2.id))
    request.mustcontain('has not been found')


def test_list_model_controller(session, app_test):
    response = app_test.get('/admin/user')
    response.mustcontain('not found')

    user1 = User(name='name', fullname='full', password='pass')
    session.add(user1)
    session.commit()

    response = app_test.get('/admin/user')
    rows = len(response.html.find_all('tr'))
    assert rows == 2

    user2 = User(name='name2', fullname='full', password='pass')
    session.add(user2)
    session.commit()

    response = app_test.get('/admin/user')
    rows = len(response.html.find_all('tr'))
    assert rows == 3


def test_routes(session, app_test):
    assert app_test.get('/admin').status == '200 OK'
    assert app_test.get('/admin/user').status == '200 OK'
    assert app_test.get('/admin/user/add').status == '200 OK'
    assert app_test.get('/admin/user/delete/1').status == '200 OK'
    assert app_test.get('/admin/product').status == '200 OK'
    assert app_test.get('/admin/product/add').status == '200 OK'
    assert app_test.get('/admin/product/delete/1').status == '200 OK'
