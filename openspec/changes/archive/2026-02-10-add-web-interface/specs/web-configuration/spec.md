## ADDED Requirements

### Requirement: Web service configuration in config.yaml

The system SHALL read web service configuration from config.yaml under "web" key.

#### Scenario: Config file contains web settings
- **WHEN** system loads config.yaml with web section
- **THEN** system reads host, port, password, jwt_secret, token_expire_days values

#### Scenario: Config file missing web section
- **WHEN** system loads config.yaml without web section
- **THEN** system merges default web configuration values
- **AND** system creates web section in config.yaml on save

### Requirement: Configurable host and port

The system SHALL allow configuring web service host and port via config.yaml.

#### Scenario: Default host is 0.0.0.0
- **WHEN** config.yaml does not specify web.host
- **THEN** system defaults to "0.0.0.0" (allows external access)

#### Scenario: Default port is 8000
- **WHEN** config.yaml does not specify web.port
- **THEN** system defaults to 8000

#### Scenario: Custom host applied
- **WHEN** config.yaml specifies web.host: "127.0.0.1"
- **THEN** system listens only on localhost

#### Scenario: Custom port applied
- **WHEN** config.yaml specifies web.port: 9000
- **THEN** system listens on port 9000

### Requirement: Password configured in config.yaml

The system SHALL read web interface password from config.yaml web.password field.

#### Scenario: Password matches config value
- **WHEN** user submits login with password from config.yaml
- **THEN** system grants access and returns JWT token

#### Scenario: Password stored in plaintext
- **WHEN** config.yaml contains web.password: "mypassword"
- **THEN** system compares login password directly with this plaintext value

### Requirement: JWT secret configurable

The system SHALL use config.yaml web.jwt_secret as signing key for JWT tokens.

#### Scenario: JWT signed with secret from config
- **WHEN** system generates JWT token
- **THEN** system signs token using web.jwt_secret value

#### Scenario: JWT verified with secret from config
- **WHEN** system validates JWT token
- **THEN** system verifies signature using web.jwt_secret value

### Requirement: Token expiration configurable

The system SHALL use config.yaml web.token_expire_days to set JWT token expiration period.

#### Scenario: Default expiration is 7 days
- **WHEN** config.yaml does not specify web.token_expire_days
- **THEN** system defaults to 7 days

#### Scenario: Custom expiration applied
- **WHEN** config.yaml specifies web.token_expire_days: 30
- **THEN** system generates tokens valid for 30 days

### Requirement: Config.py extends to support web settings

The system SHALL extend Config class with properties to access web configuration.

#### Scenario: Access web host via property
- **WHEN** code accesses config.web_host
- **THEN** system returns value from config["web"]["host"]

#### Scenario: Access web port via property
- **WHEN** code accesses config.web_port
- **THEN** system returns value from config["web"]["port"]

#### Scenario: Access web password via property
- **WHEN** code accesses config.web_password
- **THEN** system returns value from config["web"]["password"]

#### Scenario: Access JWT secret via property
- **WHEN** code accesses config.jwt_secret
- **THEN** system returns value from config["web"]["jwt_secret"]

#### Scenario: Access token expiration via property
- **WHEN** code accesses config.token_expire_days
- **THEN** system returns value from config["web"]["token_expire_days"]

### Requirement: Default config includes web section

The system SHALL include web configuration in default config template with placeholder values.

#### Scenario: New config file includes web section
- **WHEN** system generates default config.yaml
- **THEN** system includes web section with keys: host, port, password, jwt_secret, token_expire_days

#### Scenario: Default password requires change
- **WHEN** system generates default config.yaml
- **THEN** web.password value is "change_this_password" to prompt user to change

#### Scenario: Default JWT secret requires change
- **WHEN** system generates default config.yaml
- **THEN** web.jwt_secret value is "change_this_secret_key" to prompt user to change

### Requirement: Config validation warns about default values

The system SHALL warn user if default password or JWT secret values are not changed.

#### Scenario: Warning on default password
- **WHEN** system starts with web.password: "change_this_password"
- **THEN** system logs warning "警告: 请修改 config.yaml 中的 web.password"

#### Scenario: Warning on default JWT secret
- **WHEN** system starts with web.jwt_secret: "change_this_secret_key"
- **THEN** system logs warning "警告: 请修改 config.yaml 中的 web.jwt_secret"
