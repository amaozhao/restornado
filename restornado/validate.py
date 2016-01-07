# coding: utf-8

from restornado.voluptuous import MultipleInvalid


class ValidateMixin(object):

    def get_validate(self):
        arguments = self.arguments
        if getattr(self, 'GetValidateSchema', None):
            return self.validate(self.GetValidateSchema, arguments)
        return arguments

    def put_validate(self):
        arguments = self.body
        if getattr(self, 'PutValidateSchema', None):
            return self.validate(self.PutValidateSchema, arguments)
        return arguments

    def post_validate(self):
        arguments = self.body
        if getattr(self, 'PostValidateSchema', None):
            return self.validate(self.PostValidateSchema, arguments)
        return arguments

    def delete_validate(self):
        arguments = self.body
        if getattr(self, 'DeleteValidateSchema', None):
            return self.validate(self.DeleteValidateSchema, arguments)
        return arguments

    def validate(self, schema, arguments):
        try:
            return schema(arguments)
        except MultipleInvalid as e:
            return str(e)
