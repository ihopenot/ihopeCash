/**
 * Shared authentication utilities
 */

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function getAuthToken() {
    return sessionStorage.getItem('auth_token');
}

function setAuthToken(token, expireAt) {
    sessionStorage.setItem('auth_token', token);
    if (expireAt) {
        sessionStorage.setItem('token_expire_at', expireAt);
    }
}

function clearAuthToken() {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('token_expire_at');
}

function getAuthHeaders() {
    const token = getAuthToken();
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

function checkAuth() {
    const token = getAuthToken();
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function logout() {
    clearAuthToken();
    window.location.href = '/login';
}
