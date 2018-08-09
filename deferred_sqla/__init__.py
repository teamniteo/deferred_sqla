import functools
import inspect

from sqlalchemy.ext.declarative import (
    declarative_base,
    instrument_declarative,
)
from sqlalchemy import event, MetaData

from dotted_name_resolver import DottedNameResolver

import venusian

class DummyVenusian(object):
    def attach(self, *arg, **kw):
        self.attached = (arg, kw)

class DummyBase(object):
    pass

class DummyEvent(object):
    def listen(self, *arg, **kw):
        self.result = (arg, kw)

__all__ = ["Base", "model_config", "listens_for", "ConfigurationContext"]

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

SQLA_VENUSIAN_CATEGORY = 'deferred_sqla'

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

class ConfigurationContext(object):
    def __init__(self):
        self.models = {}
        
    def register_sqla_model(self, model, category='main'):
        self.models.setdefault(category, set()).add(model)

    def attach_sqla_models_to_base(self, base=None, categories=('main',)):
        if base is None:
            base = Base
        basereg = base._decl_class_registry
        for category, modelset in self.models.items():
            if not category in categories:
                continue
            for model in modelset:
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

    def scan_and_attach_sqla_models(self, pkg, base=None, categories=('main',)):
        if base is None:
            base = Base
        pkg = DottedNameResolver().maybe_resolve(pkg)
        scanner = venusian.Scanner(config=self)
        scanner.scan(pkg, categories=[SQLA_VENUSIAN_CATEGORY])
        self.attach_sqla_models_to_base(base, categories)

def model_config(*arg, **kw):
    model = None
    if len(arg) == 1 and inspect.isclass(arg[0]):
        model = arg[0]
    elif arg:
        raise ValueError(
            'Must wrap a class without arguments or must be called with '
            'keyword arguments only.'
            )
    if model is None:
        category = kw.pop('category', 'main')
    else:
        category = 'main'

    if kw:
        raise ValueError(
            'Unknown keyword arguments: %s' % ', '.join(kw.keys())
            )
    depth = 1
    if model is not None:
        # if we are using @model_config instead of @model_config(),
        # we have to supply a custom depth to venusian.attach so that
        # it doesn't think the model has been imported into the scanned
        # module from somewhere else
        depth = 2

    def wrapped(model):
        def callback(context, name, ob):
            config = context.config
            register_model = getattr(config, 'register_sqla_model', None)
            if register_model is not None:
                # might not have been included
                register_model(ob, category)
        venusian.attach(model, callback, category=SQLA_VENUSIAN_CATEGORY,
                        depth=depth)
        return model
    
    if model is None:
        return wrapped
    else:
        return wrapped(model)

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
# config.scan_and_attach_sqla_models(
#        'my.package', base=Base, categories=('main', 'other'))
#
# imperative way
#
# config = ConfigurationContext()
# config.register_sqla_model(my.package.MyModel)
# config.register_sqla_model(my.package.MyOtherModel, category='other')
# Base = declarative_base()
# config.attach_sqla_models_to_base(Base, categories=('main', 'other'))
