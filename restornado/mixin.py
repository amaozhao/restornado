# coding: utf-8

from tornado.concurrent import run_on_executor
from restornado.db.session import session_manager
from http_code import PERMISSION_ERROR


class CreateModelMixin(object):
    """
    Create a model instance.
    """

    @run_on_executor
    def create(self, *args, **kwargs):
        with session_manager() as session:
            return self.perform_create(session)

    def perform_create(self, session):
        self.schema = self.get_schema(session)
        obj = self.schema.make_instance(data=self.body)
        session.add(obj)
        session.commit()
        return obj


class ListModelMixin(object):
    """
    List a queryset.
    """

    @run_on_executor
    def list(self, *args, **kwargs):
        with session_manager() as session:
            queryset = self.get_queryset(session)
            schema = self.get_schema(session, many=True)
            if self.pagination:
                page = self.paginate_queryset(queryset)
                if page:
                    schema = self.get_schema(session, many=True)
                    return {
                        'code': 0,
                        'total': queryset.count(),
                        'data': schema.dump(page).data
                    }
            return {
                'code': 0,
                'total': queryset.count(),
                'data': schema.dump(queryset).data
            }


class RetrieveModelMixin(object):
    """
    Retrieve a model instance.
    """

    @run_on_executor
    def retrieve(self, *args, **kwargs):
        with session_manager() as session:
            instance = self.get_object(session, *args, **kwargs)
            schema = self.get_schema(session)
            return {'code': 0, 'data': schema.dump(instance).data}


class UpdateModelMixin(object):
    """
    Update a model instance.
    """

    @run_on_executor
    def update(self, *args, **kwargs):
        with session_manager() as session:
            instance = self.perform_update(
                session, self.get_object(session, *args, **kwargs))
            return {'code': 0, 'data': self.schema.dump(instance).data}

    def perform_update(self, session, instance):
        self.schema = self.get_schema(session, instance=instance)
        obj = self.schema.make_instance(data=self.body)
        session.commit()
        return obj


class DestroyManyModelMixin(object):
    """
    Destroy a model instance.
    """

    @run_on_executor
    def destroy(self, *args, **kwargs):
        with session_manager() as session:
            return self.remove(session, *args, **kwargs)

    def remove(self, session, *args, **kwargs):
        li = self.body.get('list')
        session.query(self.model).filter(
            self.model.id.in_(li)).delete(synchronize_session=False)
        session.commit()
        return {'code': 0, 'msg': u'成功'}


class DestroyModelMixin(object):
    """
    Destroy a model instance.
    """

    @run_on_executor
    def destroy(self, *args, **kwargs):
        with session_manager() as session:
            instance = self.get_object(session)
            self.perform_destroy(session, instance)
            return {'code': 0, 'msg': u'成功'}

    def perform_destroy(self, session, instance):
        instance.delete()
        session.commit()
