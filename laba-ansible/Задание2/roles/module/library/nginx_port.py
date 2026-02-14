#!/usr/bin/python
# Nginx port configurator module

import os
import re
from ansible.module_utils.basic import AnsibleModule

class NginxConfigurator:
    
    def __init__(self, module, port, config_path):
        self.module = module
        self.port = port
        self.config_path = config_path
        self.original_content = None
        
    def read_config(self):
      
        if not os.path.exists(self.config_path):
            self.module.fail_json(msg=f'Config missing: {self.config_path}')
        
        with open(self.config_path, 'r') as f:
            self.original_content = f.read()
    
    def update_port(self):
      
        pattern = re.compile(r'(listen\s+)[0-9]+;')
        return pattern.sub(f'\\g<1>{self.port};', self.original_content, count=1)
    
    def write_config(self, new_content):
      
        with open(self.config_path, 'w') as f:
            f.write(new_content)

def main():
    specs = {
        'port': {'type': 'int', 'required': True},
        'config_path': {'type': 'str', 'default': '/tmp/nginx-test/nginx-web.conf'}
    }
    
    module = AnsibleModule(argument_spec=specs, supports_check_mode=True)
    cfg = NginxConfigurator(module, module.params['port'], module.params['config_path'])
    
    try:
        cfg.read_config()
        updated = cfg.update_port()
        
        outcomes = {
            'changed': cfg.original_content != updated,
            'original': cfg.original_content[:50] + '...' if len(cfg.original_content) > 50 else cfg.original_content,
            'config': cfg.config_path,
            'port': cfg.port
        }
        
        if outcomes['changed'] and not module.check_mode:
            cfg.write_config(updated)
            outcomes['message'] = f'Port updated to {cfg.port}'
        else:
            outcomes['message'] = f'Port {cfg.port} already set'
            
        module.exit_json(**outcomes)
        
    except Exception as e:
        module.fail_json(msg=f'Operation failed: {str(e)}')

if __name__ == '__main__':
    main()