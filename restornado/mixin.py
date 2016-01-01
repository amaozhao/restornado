# coding: utf-8

from tornado.concurrent import run_on_executor
from restornado.database.session import session_manager
from http_code import PERMISSION_ERROR, PARAMTER_ERROR
# from restornado.voluptuous import MultipleInvalid
from sqlalchemy.sql import func


class CreateModelMixin(object):
    """
    Create a model instance.
    """

    @run_on_executor
    def create(self, *args, **kwargs):
        with session_manager() as session:
            if self.post_permission(session):
                if self.schema:
                    try:
                        data = self.schema(self.body)
                    except:
                        return PARAMTER_ERROR
                obj = self.perform_create(session, data)
                if isinstance(obj, self.model):
                    return {
                        'code': 0,
                        'msg': u'成功'
                    }
                else:
                    return obj
            else:
                return PERMISSION_ERROR

    def perform_create(self, session, data):
        self.schema = self.get_schema(session)
        obj = self.schema.make_instance(data=data)
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
            if self.get_permission(session):
                queryset = self.get_queryset(session)
                total = self.get_queryset_total(session, queryset)
                schema = self.get_schema(session, many=True)
                if self.pagination:
                    page = self.paginate_queryset(queryset)
                    if page:
                        schema = self.get_schema(session, many=True)
                        return {
                            'code': 0,
                            'total': total,
                            'data': schema.dump(page).data
                        }
                return {
                    'code': 0,
                    'total': total,
                    'data': schema.dump(queryset).data
                }
            else:
                return PERMISSION_ERROR

    def get_queryset_total(self, session, queryset):
        count = queryset.with_labels(
            ).statement.with_only_columns([func.count()])
        return session.execute(count).scalar()


class RetrieveModelMixin(object):
    """
    Retrieve a model instance.
    """

    @run_on_executor
    def retrieve(self, *args, **kwargs):
        with session_manager() as session:
            if self.get_permission(session):
                instance = self.get_object(session, *args, **kwargs)
                schema = self.get_schema(session)
                return {'code': 0, 'data': schema.dump(instance).data}
            else:
                return PERMISSION_ERROR


class UpdateModelMixin(object):
    """
    Update a model instance.
    """

    @run_on_executor
    def update(self, *args, **kwargs):
        with session_manager() as session:
            if self.put_permission(session):
                if self.schema:
                    try:
                        data = self.schema(self.body)
                    except:
                        return PARAMTER_ERROR
                instance = self.perform_update(
                    session, self.get_object(session, *args, **kwargs), data)
                return {'code': 0, 'data': self.schema.dump(instance).data}
            else:
                return PERMISSION_ERROR

    def perform_update(self, session, instance, data):
        self.schema = self.get_schema(session, instance=instance)
        obj = self.schema.make_instance(data=data)
        session.commit()
        return obj


class DestroyManyModelMixin(object):
    """
    Destroy a model instance.
    """

    @run_on_executor
    def destroy(self, *args, **kwargs):
        with session_manager() as session:
            if self.delete_permission(session):
                return self.remove(session, *args, **kwargs)
            else:
                return PERMISSION_ERROR

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
            if self.delete_permission(session):
                instance = self.get_object(session)
                self.perform_destroy(session, instance)
                return {'code': 0, 'msg': u'成功'}
            else:
                return PERMISSION_ERROR

    def perform_destroy(self, session, instance):
        instance.delete()
        session.commit()
