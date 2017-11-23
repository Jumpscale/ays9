from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


def _post_install(libname, libpath):
    from js9 import j

    # add this plugin to the config
    c = j.core.state.configGet('plugins', defval={})
    c[libname] = libpath
    j.core.state.configSet('plugins', c)

    print("****:%s:%s" % (libname, libpath))

    j.tools.jsloader.generate()

    # not needed to do
    # j.tools.jsloader.copyPyLibs()


class install(_install):

    def run(self):
        _install.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath),
                     msg="Running post install task")


class develop(_develop):

    def run(self):
        _develop.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath),
                     msg="Running post install task")


long_description = ""
try:
    from pypandoc import convert
    long_description = convert("README.md", 'rst')
except ImportError:
    long_description = ""


setup(
    name='JumpScale9AYS',
    version='9.2.0',
    description='Automation framework for cloud workloads ays lib',
    long_description=long_description,
    url='https://github.com/Jumpscale/ays9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'JumpScale9>=9.2.0',
        'JumpScale9Lib>=9.2.0',
        'jsonschema>=2.6.0',
        'python-jose==1.3.2',
        'sanic>=0.5.4',
        'aiohttp>=2.2.5'
    ],
    cmdclass={
        'install': install,
        'develop': develop,
        'developement': develop
    },
    scripts=['cmds/ays'],
)
