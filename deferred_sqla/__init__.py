import functools

from sqlalchemy.ext.declarative import instrument_declarative
from sqlalchemy import event

from dotted_name_resolver import DottedNameResolver

import venusian

__all__ = ["model_config", "listens_for", "ConfigurationContext"]

SQLA_VENUSIAN_CATEGORY = 'deferred_sqla'

class ConfigurationContext(object):
    def __init__(self):
        self.models = set()
        
    def register_sqla_model(self, model, category='main'):
        self.models.add(model)

    def attach_sqla_models_to_base(self, base):
        basereg = base._decl_class_registry
        for model in self.models:
            if '_decl_class_registry' in model.__dict__:
                modelreg = model._decl_class_registry
                if modelreg == basereg:
                    continue
                else:
                    raise ValueError(
                        "Tried to attach model %s to two different Bases: "
                        "%s vs. %s " % (modelreg, basereg),
                        )
            instrument_declarative(model, basereg, base.metadata)

    def scan_and_attach_sqla_models(self, pkg, base):
        pkg = DottedNameResolver().maybe_resolve(pkg)
        scanner = venusian.Scanner(config=self)
        scanner.scan(pkg, categories=[SQLA_VENUSIAN_CATEGORY])
        self.attach_sqla_models_to_base(base)

def model_config(model):
    def callback(context, name, ob):
        config = context.config
        register_model = getattr(config, 'register_sqla_model', None)
        if register_model is not None:
            # might not have been included
            register_model(ob)
    venusian.attach(model, callback, category=SQLA_VENUSIAN_CATEGORY)
    return model
    
def listens_for(target, identifier, *args, **kwargs):
    """Deferred listens_for decorator that calls sqlalchemy.event.listen
    """
    def deco(wrapped):
        def callback(scanner, _name, wrapped):
            wrapped = functools.partial(wrapped, scanner.config)
            event.listen(target, identifier, wrapped, *args, **kwargs)

        venusian.attach(wrapped, callback)

        return wrapped

    return deco

# declarative way
#
# config = ConfigurationContext()
# Base = declarative_base()
# config.scan_and_attach_sqla_models('my.package', base=Base)
#
# imperative way
#
# config = ConfigurationContext()
# config.register_sqla_model(my.package.MyModel)
# config.register_sqla_model(my.package.MyOtherModel)
# Base = declarative_base()
# config.attach_sqla_models_to_base(Base)
