import importlib
import unittest

class TestPackageScans(unittest.TestCase):
    def _makeConfig(self):
        from deferred_sqla import ConfigurationContext
        config = ConfigurationContext()
        return config

    def setUp(self):
        # reload the module to remove venusian callbacks juuust in case
        from .pkgs import modelcfg
        importlib.reload(modelcfg)
        self.modelcfg = modelcfg

    tearDown = setUp
        
    def test_scan_and_attach(self):
        from sqlalchemy.ext.declarative import declarative_base
        base = declarative_base()
        config = self._makeConfig()
        config.scan_and_attach_sqla_models('tests.pkgs.modelcfg', base=base)
        
        models = set([
            self.modelcfg.MyMainModel1,
            self.modelcfg.MyMainModel2,
            self.modelcfg.MyMainModel3,
        ])

        self.assertEqual(config.models, models)
        
        for model in models:
            self.assertTrue(
                model._decl_class_registry is base._decl_class_registry
            )

