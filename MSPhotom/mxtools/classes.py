# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 15:13:02 2024

@author: mbmad
"""


def create_monitored_class(cls):
    """
    Created a 'monitored' version of a given class.
    
    Monitored classes allow insertion of methods before and after the execution
    of any (non-dunder) method

    Returns
    -------
    cls
        Monitored class.

    """
    def create_wrapped_init(init_method):
        def _wrapped_init(self, *args, **kwargs):
            self.monitor_trigger_on_call = {}
            self.monitor_trigger_on_return = {}
            self._report = kwargs.get('report', False)
            init_method(self, *args, **kwargs)
        return _wrapped_init

    def create_wrapped_method(name, method):
        def wrapped_method(self, *args, **kwargs):
            try:
                if self._report:
                    print(f'method {name} triggered')
    
                # Ensure args and kwargs are not None
                args = args or ()
                kwargs = kwargs or {}
    
                # Handle monitor trigger on call
                if name in self.monitor_trigger_on_call:
                    modified_args = self.monitor_trigger_on_call[name](self, *args, **kwargs)
                    # If modified_args is None, keep original args and kwargs
                    if modified_args is not None:
                        args, kwargs = modified_args
                    if self._report:
                        print('    Call modified')
            except Exception as error:
                print(f'Unknown error during monitoring of precall for {name}')
                print(error)
            
            result = method(self, *args, **kwargs)
            
            try:
                # Handle monitor trigger on return
                if name in self.monitor_trigger_on_return:
                    modified_result = self.monitor_trigger_on_return[name](self, result)
                    # If modified_result is None, keep the original result
                    if modified_result is not None:
                        result = modified_result
                    if self._report:
                        print('    Return modified')
            except Exception as error:
                print(f'Unknown error during monitoring of return for {name}')
                print(error)
            
            return result
        return wrapped_method


    def monitor_method_call(self, method_name, triggered_function):
        self.monitor_trigger_on_call[method_name] = triggered_function

    def monitor_method_return(self, method_name, triggered_function):
        self.monitor_trigger_on_return[method_name] = triggered_function

    def passthroughmethod(function, *fargs, **fkwargs):
        def wrappedfunc(self, *args, **kwargs):
            function(*fargs, **fkwargs)
            return args or (), kwargs or {}
        return wrappedfunc

    def print_on_call(self, method_name, msg):
        self.monitor_trigger_on_call[method_name] = passthroughmethod(
            print, msg)

    def print_on_return(self, method_name, msg):
        self.monitor_trigger_on_return[method_name] = passthroughmethod(
            print, msg)

    setattr(cls, '__init__', create_wrapped_init(cls.__dict__['__init__']))
    setattr(cls, 'monitor_method_call', monitor_method_call)
    setattr(cls, 'monitor_method_return', monitor_method_return)
    setattr(cls, 'monitor_print_on_call', print_on_call)
    setattr(cls, 'monitor_print_on_return', print_on_return)
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and '__' not in attr_name and 'monitor' not in attr_name:
            setattr(cls, attr_name, create_wrapped_method(
                attr_name, attr_value))
    return cls


class MonitoredClass:
    """
    Dummy Class used for convenient autocomplete of monitored class methods
    """
    def monitor_method_call(self, method_name, triggered_function):
        pass

    def monitor_method_return(self, method_name, triggered_function):
        pass

    def monitor_print_on_call(self, method_name, msg):
        pass

    def monitor_print_on_return(self, method_name, msg):
        pass
