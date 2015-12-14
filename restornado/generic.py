# coding: utf-8
"""
Generic views that provide commonly needed behaviour.
"""
from __future__ import unicode_literals
import json
from tornado.web import RequestHandler
from tornado import gen
from tornado.escape import url_unescape
from restornado.mixin import (
    CreateModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, DestroyManyModelMixin
)
from modules.account.models import User, Permission, Role
from restornado.renderers import JSONRenderer


class BaseRequestHandler(RequestHandler):

    def initialize(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    @property
    def executor(self):
        return self.application.executor

    @property
    def redis(self):
        return self.application.redis

    @property
    def current_user(self):
        return None

    def get_current_user(self, session):
        userId = self.request.headers.get('userId')
        try:
            return session.query(User).filter(
                User.id == userId,
                User.status.is_(True)).first()
        except:
            return None

    @property
    def body(self):
        try:
            return json.loads(url_unescape(self.request.body))
        except:
            return {}


class GenericAPIView(BaseRequestHandler):

    """
    Base class for all other generic views.
    """
    queryset = None
    schema_class = None
    lookup_field = 'id'
    lookup_url_kwarg = None
    pagination = False
    permission_class = Permission
    model = None

    def get_queryset(self, session):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        return queryset

    def get_object(self, session, *args, **kwargs):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.get_queryset(session)
        obj = queryset.filter_by(**kwargs).first()
        return obj

    def get_schema(self, session, *args, **kwargs):
        schema_class = self.get_schema_class()
        kwargs.update(**self.get_schema_context(session))
        return schema_class(*args, **kwargs)

    def get_schema_class(self):
        assert self.schema_class is not None, (
            "'%s' should either include a `schema_class` attribute, "
            "or override the `get_schema_class()` method."
            % self.__class__.__name__
        )

        return self.schema_class

    def get_schema_context(self, session):
        return {
            'session': session,
            'redis': self.redis,
            'view': self
        }

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        page = self.get_page() - 1
        if not isinstance(queryset, list):
            data = queryset.offset(page * self.get_page_size())
            return data.limit(self.get_page_size())
        return list()

    def get_page_size(self):
        pageSize = self.get_argument('pageSize', None)
        if pageSize:
            try:
                pageSize = int(pageSize)
                return pageSize
            except (KeyError, ValueError):
                pass

        return 10

    def get_page(self):
        page = self.get_argument('page', None)
        if page:
            try:
                return int(page)
            except (KeyError, ValueError):
                pass

        return 1

    def get_permission(self, session):
        token = self.request.headers.get('Authorization')
        userId = self.request.headers.get('userId')
        if not (userId and token):
            return False
        perm_code = self.permissions.get('get', None)
        query = session.query(Role).filter(
            Role.users.any(id=userId),
            Role.permissions.any(perm_code=perm_code))
        return session.query(query.exists()).scalar()

    def post_permission(self, session):
        token = self.request.headers.get('Authorization')
        userId = self.request.headers.get('userId')
        if not (userId and token):
            return False
        perm_code = self.permissions.get('post', None)
        query = session.query(Role).filter(
            Role.users.any(id=userId),
            Role.permissions.any(perm_code=perm_code))
        return session.query(query.exists()).scalar()

    def put_permission(self, session):
        token = self.request.headers.get('Authorization')
        userId = self.request.headers.get('userId')
        if not (userId and token):
            return False
        perm_code = self.permissions.get('put', None)
        query = session.query(Role).filter(
            Role.users.any(id=userId),
            Role.permissions.any(perm_code=perm_code))
        return session.query(query.exists()).scalar()

    def delete_permission(self, session):
        token = self.request.headers.get('Authorization')
        userId = self.request.headers.get('userId')
        if not (userId and token):
            return False
        perm_code = self.permissions.get('delete', None)
        query = session.query(Role).filter(
            Role.users.any(id=userId),
            Role.permissions.any(perm_code=perm_code))
        return session.query(query.exists()).scalar()


class CreateAPIView(CreateModelMixin, GenericAPIView):

    """
    Concrete view for creating a model instance.
    """
    @gen.coroutine
    def post(self, *args, **kwargs):
        data = yield self.create(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()


class ListAPIView(ListModelMixin, GenericAPIView):

    """
    Concrete view for listing a queryset.
    """

    @gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.list(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()


class RetrieveAPIView(RetrieveModelMixin, GenericAPIView):

    """
    Concrete view for retrieving a model instance.
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.retrieve(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()


class DestroyAPIView(DestroyModelMixin, GenericAPIView):

    """
    Concrete view for deleting a model instance.
    """

    def delete(self, *args, **kwargs):
        return self.destroy(*args, **kwargs)


class UpdateAPIView(UpdateModelMixin, GenericAPIView):

    """
    Concrete view for updating a model instance.
    """
    @gen.coroutine
    def put(self, *args, **kwargs):
        data = yield self.update(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()


class ListCreateAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):

    """
    Concrete view for listing a queryset or creating a model instance.
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.list(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()

    @gen.coroutine
    def post(self, *args, **kwargs):
        data = yield self.create(*args, **kwargs)
        if data.get('code') == 0:
            self.write(JSONRenderer().render({'code': 0, 'msg': u'成功'}))
        else:
            self.write(JSONRenderer().render(data))
        self.finish()


class ListCreateDeleteAPIView(ListCreateAPIView, DestroyManyModelMixin):
    @gen.coroutine
    def delete(self, *args, **kwargs):
        data = yield self.destroy(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()


class RetrieveUpdateAPIView(RetrieveModelMixin,
                            UpdateModelMixin,
                            GenericAPIView):

    """
    Concrete view for retrieving, updating a model instance.
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.retrieve(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()

    @gen.coroutine
    def put(self, *args, **kwargs):
        data = yield self.update(*args, **kwargs)
        if data.get('code', 0) == 0:
            self.write(JSONRenderer().render({'code': 0, 'msg': u'成功'}))
        else:
            self.write(JSONRenderer().render(data))
        self.finish()


class RetrieveDestroyAPIView(RetrieveModelMixin,
                             DestroyModelMixin,
                             GenericAPIView):

    """
    Concrete view for retrieving or deleting a model instance.
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.retrieve(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()

    @gen.coroutine
    def delete(self, *args, **kwargs):
        data = yield self.destroy(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()


class RetrieveUpdateDestroyAPIView(RetrieveModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin, GenericAPIView):

    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.retrieve(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()

    @gen.coroutine
    def put(self, *args, **kwargs):
        data = yield self.update(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()

    def patch(self, *args, **kwargs):
        return self.partial_update(*args, **kwargs)

    @gen.coroutine
    def delete(self, *args, **kwargs):
        data = yield self.destroy(*args, **kwargs)
        self.write(JSONRenderer().render(data))
        self.finish()
