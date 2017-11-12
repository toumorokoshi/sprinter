import os
import sprinter.lib as lib


def execute_commmon_functionality(formula_instance):
    install_directory = formula_instance.directory.install_directory(formula_instance.feature_name)
    cwd = install_directory if os.path.exists(install_directory) else None
    if formula_instance.target.has('env'):
        formula_instance.directory.add_to_env(formula_instance.target.get('env'))
    if formula_instance.target.has('rc'):
        formula_instance.directory.add_to_rc(formula_instance.target.get('rc'))
    if formula_instance.target.has('gui'):
        formula_instance.directory.add_to_gui(formula_instance.target.get('gui'))
    if formula_instance.target.has('command'):
        lib.call(formula_instance.target.get('command'), shell=True, cwd=cwd)
