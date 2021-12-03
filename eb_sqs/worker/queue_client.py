from __future__ import absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod


class QueueClientException(Exception):
    pass


class QueueDoesNotExistException(QueueClientException):
    def __init__(self, queue_name):
        # type: (unicode) -> None
        super(QueueDoesNotExistException, self).__init__()
        self.queue_name = queue_name


class QueueClient(object):
    __metaclass__ = ABCMeta

    def __init__(self, group_id):
        # type: (unicode) -> None
        super(QueueClient, self).__init__()
        self._group_id = group_id

    @abstractmethod
    def add_message(self, queue_name, group_id, msg, delay):
        # type: (unicode, unicode, int) -> None
        pass
