# coding=utf-8

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/19/16'


class DummySourceAPI(object):

    @classmethod
    def get_aggregate_report(cls, filename):
        return open(filename).read()
