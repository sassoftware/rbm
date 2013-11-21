Puppet::Type.newtype(:mirror_user) do
    ensurable

    newparam(:name) do
      desc "Repository user name"
      isnamevar
    end

    newparam(:salt) do
      desc "User's password salt, hex-encoded"
    end

    newparam(:digest) do
      desc "User's password digest, hex-encoded"
    end

    newparam(:permission) do
      desc "User permission level: admin, anonymous, or mirror"
    end

    autorequire(:service) do
      [ 'gunicorn' ]
    end
end
