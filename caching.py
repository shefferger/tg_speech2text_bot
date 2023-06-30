import datetime

values = dict()


class Cache:
    @staticmethod
    def cache(delta: int):
        def decorator(func):
            def wrapper(var):
                ctime = datetime.datetime.now()
                if var in values.keys() and \
                        values[var]['expiration'] > ctime:
                    result = values[var]['result']
                else:
                    result = func(var)
                    values[var] = dict(expiration=ctime + datetime.timedelta(seconds=delta), result=result)
                return result
            return wrapper
        return decorator
