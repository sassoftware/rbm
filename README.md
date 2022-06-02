# SAS App Engine Update Service -- Archived Repository
**Notice: This repository is part of a Conary/rpath project at SAS that is no longer supported or maintained. Hence, the repository is being archived and will live in a read-only state moving forward. Issues, pull requests, and changes will no longer be accepted.**
 
Overview
--------
An *Update Service* is a preconfigured Conary repository used for distributing
updates to client systems. It can operate in two modes: mirror mode or proxy
mode. In proxy mode the Update Service is backed by an App Engine for which it
acts as a caching proxy. In mirror mode it is a repository which must have
content pushed into it by the rBuilder.

Components of an Update Service include:

* *Conary* repository or caching proxy
* conaryrc generator that Conary clients can prefetch or include via HTTP to
  get a complete list of repositoryMap or proxyMap lines to make use of the
  Update Service
* A *rmake3* worker node for deploying EBS images to Amazon EC2
* Registration service and image download service, used internally by SAS
* Preconfigured PostgreSQL, pgbouncer, nginx, gunicorn
* Tools and puppet modules for provisioning
