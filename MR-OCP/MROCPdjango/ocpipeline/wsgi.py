
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created by Disa Mhembere
# Email: disa@jhu.edu
"""
WSGI config for ocpipeline project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application

os.sys.path += [ os.path.abspath(os.path.join(os.path.dirname(__file__), ".." )),  os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")) ]
os.environ["DJANGO_SETTINGS_MODULE"] = "ocpipeline.settings"
os.environ["HOME"] = "/tmp"


env_variables_to_pass = ["M2G_HOME"]
def application(environ, start_response):
  # pass the WSGI environment variables on through to os.environ
  for var in env_variables_to_pass:
      os.environ[var] = environ.get(var, '')
  return get_wsgi_application()(environ, start_response)
