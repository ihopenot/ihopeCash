## MODIFIED Requirements

### Requirement: All API endpoints require authentication

The system SHALL protect all API endpoints (except /api/auth/login and /api/setup/status) with JWT token authentication. Setup API endpoints (/api/setup/defaults, /api/setup/complete) SHALL also require authentication.

#### Scenario: API request with valid token
- **WHEN** user sends request with valid JWT token in Authorization header
- **THEN** system processes the request normally

#### Scenario: API request with invalid token
- **WHEN** user sends request with invalid or expired JWT token
- **THEN** system returns 401 Unauthorized error

#### Scenario: API request without token
- **WHEN** user sends request without Authorization header
- **THEN** system returns 401 Unauthorized error

#### Scenario: Setup status endpoint does not require authentication
- **WHEN** unauthenticated user requests GET /api/setup/status
- **THEN** system returns the setup status normally without requiring authentication

#### Scenario: Setup API endpoints require authentication
- **WHEN** unauthenticated user requests GET /api/setup/defaults or POST /api/setup/complete
- **THEN** system returns 401 Unauthorized error

## ADDED Requirements

### Requirement: Authentication works with env.yaml password during setup

During setup mode (config.yaml does not exist), the system SHALL authenticate users using the password from env.yaml's web.password field.

#### Scenario: Login during setup mode
- **WHEN** setup_required is True
- **AND** user submits the password from env.yaml's web.password
- **THEN** system returns a valid JWT token

#### Scenario: JWT secret from env.yaml during setup
- **WHEN** setup_required is True
- **THEN** JWT tokens are signed using jwt_secret from env.yaml
