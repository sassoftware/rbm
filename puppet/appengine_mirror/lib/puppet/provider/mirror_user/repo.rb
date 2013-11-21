require 'pathname'
require Pathname.new(__FILE__).dirname.dirname.expand_path + 'mirror'

Puppet::Type.type(:mirror_user).provide(:repo, :parent => Puppet::Provider::Mirror) do

    def self.prefetch(resources)
        instances.each do |prov|
            if res = resources[prov.name.to_s]
                res.provider = prov
            end
        end
    end

    def self.instances
        admin(['user-list']).map {|user| new({
            :ensure                 => :present,
            :name                   => user['user-name'],
            :permission             => user['permission'],
            :salt                   => user['salt'],
            :digest                 => user['password'],
            })}
    end

    def exists?
        # If puppet wants us gone, match anything with the given name
        return !@property_hash.empty? if @resource[:ensure] != :present
        # Otherwise make sure all properties match
        for key in [:name, :permission, :salt, :digest]
            if @resource[key] != @property_hash[key]
                return false
            end
        end
        return !@property_hash.empty?
    end

    def create
        admin(['user-add',
                 '--user-name', resource[:name],
                 '--permission', resource[:permission],
                 '--salt', resource[:salt],
                 '--password', resource[:digest],
                  ])
    end

    def destroy
        admin ['user-delete', '--user-name', resource[:name]]
    end

end
