## ADDED Requirements

### Requirement: User can log in with password

The system SHALL provide a login interface that accepts a password and returns a JWT token upon successful authentication.

#### Scenario: Successful login with correct password
- **WHEN** user submits correct password from config.yaml
- **THEN** system returns a valid JWT token with 7-day expiration

#### Scenario: Failed login with incorrect password
- **WHEN** user submits incorrect password
- **THEN** system returns 401 Unauthorized error with message "密码错误"

#### Scenario: Login page displayed for unauthenticated users
- **WHEN** user accesses any page without valid token
- **THEN** system redirects to /login page

### Requirement: All API endpoints require authentication

The system SHALL protect all API endpoints (except /api/auth/login) with JWT token authentication.

#### Scenario: API request with valid token
- **WHEN** user sends request with valid JWT token in Authorization header
- **THEN** system processes the request normally

#### Scenario: API request with invalid token
- **WHEN** user sends request with invalid or expired JWT token
- **THEN** system returns 401 Unauthorized error

#### Scenario: API request without token
- **WHEN** user sends request without Authorization header
- **THEN** system returns 401 Unauthorized error

### Requirement: WebSocket connections require authentication

The system SHALL require JWT token for WebSocket connections via query parameter.

#### Scenario: WebSocket connection with valid token
- **WHEN** user connects to WebSocket with valid token in query parameter
- **THEN** system accepts the connection and allows message exchange

#### Scenario: WebSocket connection with invalid token
- **WHEN** user connects to WebSocket with invalid or expired token
- **THEN** system rejects the connection with 401 error

### Requirement: JWT tokens have configurable expiration

The system SHALL generate JWT tokens with expiration time configurable in config.yaml (default 7 days).

#### Scenario: Token valid within expiration period
- **WHEN** user makes request with token before expiration time
- **THEN** system accepts the token

#### Scenario: Token expired
- **WHEN** user makes request with token after expiration time
- **THEN** system returns 401 Unauthorized error with message "Token 已过期"

### Requirement: Token stored in browser localStorage

The system SHALL store JWT token in browser localStorage after successful login.

#### Scenario: Token persists across page reloads
- **WHEN** user logs in successfully and reloads the page
- **THEN** system reads token from localStorage and maintains logged-in state

#### Scenario: Logout clears token
- **WHEN** user clicks logout button
- **THEN** system removes token from localStorage and redirects to login page
