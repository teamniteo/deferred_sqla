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
        
    def test_scan_and_attach_none_based_due_to_category_implicit_base(self):
        config = self._makeConfig()
        config.scan_and_attach_sqla_models(
            'tests.pkgs.modelcfg', categories=('wontbefound,'))
        
        mainmodels = set([
            self.modelcfg.MyMainModel1,
            self.modelcfg.MyMainModel2,
            self.modelcfg.MyMainModel3,
        ])
        othermodels = set([
            self.modelcfg.MyOtherModel1,
            self.modelcfg.MyOtherModel2,
        ])
        for model in mainmodels.union(othermodels):
            self.assertFalse('_decl_class_registry' in model.__dict__, model)

        self.assertEqual(len(config.models), 2)
        self.assertEqual(config.models['main'], mainmodels)
        self.assertEqual(config.models['other'], othermodels)
        
    def test_scan_and_attach_all_based(self):
        from deferred_sqla import Base
        config = self._makeConfig()
        config.scan_and_attach_sqla_models(
            'tests.pkgs.modelcfg', categories=('main', 'other')
        )
        
        mainmodels = set([
            self.modelcfg.MyMainModel1,
            self.modelcfg.MyMainModel2,
            self.modelcfg.MyMainModel3,
        ])
        othermodels = set([
            self.modelcfg.MyOtherModel1,
            self.modelcfg.MyOtherModel2,
        ])
        for model in mainmodels.union(othermodels):
            self.assertTrue(
                model._decl_class_registry is Base._decl_class_registry
            )

        self.assertEqual(len(config.models), 2)
        self.assertEqual(config.models['main'], mainmodels)
        self.assertEqual(config.models['other'], othermodels)

    def test_scan_and_attach_all_based_explicit_base(self):
        from sqlalchemy.ext.declarative import declarative_base
        from deferred_sqla import Base
        base = declarative_base()
        config = self._makeConfig()
        config.scan_and_attach_sqla_models(
            'tests.pkgs.modelcfg', base=base, categories=('main', 'other')
        )
        
        mainmodels = set([
            self.modelcfg.MyMainModel1,
            self.modelcfg.MyMainModel2,
            self.modelcfg.MyMainModel3,
        ])
        othermodels = set([
            self.modelcfg.MyOtherModel1,
            self.modelcfg.MyOtherModel2,
        ])
        for model in mainmodels.union(othermodels):
            self.assertTrue(
                model._decl_class_registry is base._decl_class_registry
            )
            self.assertFalse(
                model._decl_class_registry is Base._decl_class_registry
            )

        self.assertEqual(len(config.models), 2)
        self.assertEqual(config.models['main'], mainmodels)
        self.assertEqual(config.models['other'], othermodels)
        
