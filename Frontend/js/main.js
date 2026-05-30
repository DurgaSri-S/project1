// Utilities
window.showToast = (msg, type = 'success') => {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.className = `show ${type}`;
    if (type === 'error') {
        toast.classList.add('error');
    }
    setTimeout(() => {
        toast.className = '';
    }, 3000);
};

// State
let currentUser = null;

const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
        try {
            currentUser = await api.auth.me();
            updateNavigation();
        } catch (error) {
            console.error('Auth expired or invalid', error);
            localStorage.removeItem('token');
        }
    }
};

const updateNavigation = () => {
    const loginLink = document.getElementById('nav-login');
    const registerLink = document.getElementById('nav-register');
    const dashboardLink = document.getElementById('nav-dashboard');
    const adminLink = document.getElementById('nav-admin');
    const tutorLink = document.getElementById('nav-tutor');
    const logoutBtn = document.getElementById('nav-logout');

    if (currentUser) {
        if(loginLink) loginLink.classList.add('hidden');
        if(registerLink) registerLink.classList.add('hidden');
        
        if (currentUser.role === 'admin') {
            if(adminLink) adminLink.classList.remove('hidden');
            if(dashboardLink) dashboardLink.classList.add('hidden');
            if(tutorLink) tutorLink.classList.add('hidden');
        } else if (currentUser.role === 'tutor') {
            if(tutorLink) tutorLink.classList.remove('hidden');
            if(adminLink) adminLink.classList.add('hidden');
            if(dashboardLink) dashboardLink.classList.add('hidden');
        } else {
            if(dashboardLink) dashboardLink.classList.remove('hidden');
            if(adminLink) adminLink.classList.add('hidden');
            if(tutorLink) tutorLink.classList.add('hidden');
            
            // Explicitly show assignments/payments in dashboard (handled via hashes or tabs usually, but let's just make sure dashboard is visible)
        }
        
        if(logoutBtn) logoutBtn.classList.remove('hidden');
    } else {
        if(loginLink) loginLink.classList.remove('hidden');
        if(registerLink) registerLink.classList.remove('hidden');
        if(dashboardLink) dashboardLink.classList.add('hidden');
        if(adminLink) adminLink.classList.add('hidden');
        if(logoutBtn) logoutBtn.classList.add('hidden');
    }
};

const handleLogout = () => {
    localStorage.removeItem('token');
    currentUser = null;
    window.location.href = '/';
};

// Main Initialization
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();

    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }
});
