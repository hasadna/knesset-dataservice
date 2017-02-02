class MockDataserviceObject(object):

    def __init__(self, dataservice_class, **kwargs):
        for field_name, field in dataservice_class.get_fields().iteritems():
            setattr(self, field_name, kwargs.get(field_name, None))
