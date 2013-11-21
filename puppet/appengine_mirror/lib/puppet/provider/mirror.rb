#
# Copyright (c) SAS Institute Inc.
#

require 'json'


class Puppet::Provider::Mirror < Puppet::Provider
  initvars
  commands :mirror_admin => '/usr/sbin/mirror-admin'

  def self.admin(args)
      cmd = [ command(:mirror_admin), '--json' ] + args
      raw = Puppet::Util::Execution.execute(cmd, :failonfail => true)
      JSON.parse(raw)
  end
  def admin(args)
      self.class.admin(args)
  end
end
