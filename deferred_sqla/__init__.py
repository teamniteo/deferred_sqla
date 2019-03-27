import functools

from sqlalchemy.ext.declarative import instrument_declarative

from dotted_name_resolver import DottedNameResolver

import venusian

__all__ = ["model_config", "ConfigurationContext"]

SQLA_VENUSIAN_CATEGORY = 'deferred_sqla'

def prep_config_with_modelreg(wrapped):
    @functools.wraps(wrapped)
    def prep(config, *arg, **kw):
        config.__dict__.setdefault('_deferred_sqla_models', set())
        return wrapped(config, *arg, **kw)
    return prep

# Configurator API methods; this is written so awkwardly because we
# reuse the top two functions below as Pyramid Configurator directives in
# pyramid_deferred_sqla; these are "semi-private" APIs, so are not listed
# in __all__

@prep_config_with_modelreg
def register_sqla_models(config, *models):
    config._deferred_sqla_models.update(models)

@prep_config_with_modelreg
def attach_sqla_models_to_base(config, base):
    basereg = base._decl_class_registry
    for model in config._deferred_sqla_models:
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
    return config._deferred_sqla_models

def scan_and_attach_sqla_models(config, pkg, base):
    pkg = DottedNameResolver().maybe_resolve(pkg)
    scanner = venusian.Scanner(config=config)
    scanner.scan(pkg, categories=[SQLA_VENUSIAN_CATEGORY])
    config.attach_sqla_models_to_base(base)

# /Configurator API methods


# standalone configuration context
class ConfigurationContext(object):
    register_sqla_models = register_sqla_models
    attach_sqla_models_to_base = attach_sqla_models_to_base
    scan_and_attach_sqla_models = scan_and_attach_sqla_models


def model_config(model):
    def callback(context, name, ob):
        config = context.config
        register_model = getattr(config, 'register_sqla_models', None)
        if register_model is not None:
            # might not have been included
            register_model(ob)
    venusian.attach(model, callback, category=SQLA_VENUSIAN_CATEGORY)
    return model
    
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
