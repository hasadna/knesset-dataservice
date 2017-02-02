import logging


from django_nose import NoseTestSuiteRunner


class KnessetDataDjangoTestRunner(NoseTestSuiteRunner):

    def setup_test_environment(self, **kwargs):
        # Disabling debug/info in testing
        logging.disable(logging.WARNING)
        return super(KnessetDataDjangoTestRunner, self).setup_test_environment(**kwargs)
