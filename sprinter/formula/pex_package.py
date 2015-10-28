"""
the pex formula is for generating a pex python executable. It's intended to
replace the existing eggscript formula, which has had issues with it's virtualenv.

https://github.com/pantsbuild/pex

[sprinter]
eggs = sprinter
entry_point = sprinter.install:main
executable_name = sprinter
"""
from __future__ import unicode_literals

import os
from sprinter.formula.base import FormulaBase
from pex.interpreter import PythonInterpreter
from pex.pex_builder import PEXBuilder
from pex.resolvable import Resolvable
from pex.resolver import Resolver
from pex.resolver_options import ResolverOptionsBuilder
from pex.bin.pex import interpreter_from_options, configure_clp


class PexFormula(FormulaBase):

    required_options = FormulaBase.required_options + [
        "eggs", "entry_point", "executable_name"
    ]

    def install(self):
        self._build()

    def update(self):
        self._build()

    @property
    def install_directory(self):
        return self.directory.install_directory(self.feature_name)

    def _build(self):
        target_path = os.path.join(self.install_directory,
                                   self.target.get("executable_name"))
        parser, resolver_options_builder = configure_clp()
        pex_builder = PEXBuilder(
            interpreter=self._get_interpreter(parser)
        )
        pex_builder.set_entry_point(self.target.get("entry_point"))
        for dist in self._get_distributions(resolver_options_builder):
            pex_builder.add_distribution(dist)
            pex_builder.add_requirement(dist.as_requirement())
        pex_builder.build(target_path)
        self.directory.symlink_to_bin(self.target.get("executable_name"),
                                      target_path)

    def _get_distributions(self, resolver_options_builder):
        eggs = self.target.get("eggs").splitlines()
        resolvables = [Resolvable.get(e, resolver_options_builder) for e in eggs]
        resolver = Resolver()
        return resolver.resolve(resolvables)

    def _get_interpreter(self, parser):
        options, reqs = parser.parse_args(args=[
            "-e", self.target.get("executable_name"),
            "--wheel",
        ])
        return interpreter_from_options(options)
