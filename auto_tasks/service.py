import importlib
import logging

from auto_tasks.base_service import BaseAutoTaskService, NoopTaskService
from auto_tasks.exceptions import RetryableTaskException
from eb_sqs.decorators import task
from eb_sqs.worker.worker_exceptions import MaxRetriesReachedException

logger = logging.getLogger(__name__)


@task()
def _auto_task_wrapper(module_name, class_name, func_name, *args, **kwargs):
    try:
        logger.debug(
            'Invoke _auto_task_wrapper with module: %s class: %s func: %s args: %s and kwargs: %s',
            module_name,
            class_name,
            func_name,
            args,
            kwargs
        )

        module = importlib.import_module(module_name)  # import module
        class_ = getattr(module, class_name)  # find class
        instance = class_(auto_task_service=NoopTaskService())  # instantiate class using empty AutoTaskService
        getattr(instance, func_name)(*args, **kwargs)  # invoke method on instance
    except RetryableTaskException as exc:
        try:
            retry_kwargs = {}
            if 'execute_inline' in kwargs:
                retry_kwargs['execute_inline'] = kwargs['execute_inline']

            if exc.delay is not None:
                retry_kwargs['delay'] = exc.delay

            if exc.count_retries is not None:
                retry_kwargs['count_retries'] = exc.count_retries

            _auto_task_wrapper.retry(**retry_kwargs)
        except MaxRetriesReachedException:
            logger.error('Reached max retries in auto task {}.{}.{} with error: {}'.format(module_name, class_name, func_name, repr(exc)))


class AutoTaskService(BaseAutoTaskService):
    def register_task(self, method, queue_name=None, max_retries=None):
        # type: (Any, str, int) -> None
        instance = method.im_self
        class_ = instance.__class__
        func_name = method.func_name

        def _auto_task_wrapper_invoker(*args, **kwargs):
            if queue_name is not None:
                kwargs['queue_name'] = queue_name

            if max_retries is not None:
                kwargs['max_retries'] = max_retries

            _auto_task_wrapper.delay(
                class_.__module__,
                class_.__name__,
                func_name,
                *args, **kwargs
            )

        setattr(instance, func_name, _auto_task_wrapper_invoker)
