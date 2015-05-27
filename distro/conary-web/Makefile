#
# Copyright (c) SAS Institute Inc.
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


all: default-all

install: default-install
	install -D -m0644 corplogo.png $(DESTDIR)/usr/share/conary/web-common/images/corplogo.png
	install -D -m0644 prodlogo.gif $(DESTDIR)/usr/share/conary/web-common/images/prodlogo.gif
	install -D -m0644 custom.css $(DESTDIR)/usr/share/conary/web-common/css/custom.css

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
