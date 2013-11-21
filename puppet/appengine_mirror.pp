class { 'appengine_mirror':
    web_enabled => false,
    zone => 'Local rBuilder',
    # Set if node functionality is desired, leave unset for standalone operation
    #xmpp_host => 'app.engine.hostname',
    # Set for proxy mode, leave unset for mirror mode
    #proxy_upstream => 'app.engine.hostname',
}

mirror_user { 'anonymous':
    ensure => present,
    permission => 'anonymous',
    salt => '9a1b3988',
    digest => '8b4d911930f4616c68d261de89ed3b34',
}

#mirror_user { 'admin':
#    ensure => present,
#    permission => 'admin',
#    salt => '',
#    digest => '',
#}
