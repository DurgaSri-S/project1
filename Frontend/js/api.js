const API_BASE = '/api';

const authHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

const handleResponse = async (res) => {
    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || 'API request failed');
    }
    return res.json();
};

const api = {
    auth: {
        login: async (email, password) => {
            const formData = new URLSearchParams();
            formData.append('username', email); 
            formData.append('password', password);
            
            const res = await fetch(`${API_BASE}/users/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            return handleResponse(res);
        },
        register: async (email, fullName, password, role = 'student') => {
            const res = await fetch(`${API_BASE}/users/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, full_name: fullName, password, role })
            });
            return handleResponse(res);
        },
        me: async () => {
            const res = await fetch(`${API_BASE}/users/me`, {
                headers: authHeader()
            });
            return handleResponse(res);
        }
    },
    users: {
        getAll: async () => {
            const res = await fetch(`${API_BASE}/users/`, { headers: authHeader() });
            return handleResponse(res);
        },
        updateRole: async (userId, role) => {
            const res = await fetch(`${API_BASE}/users/${userId}/role`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify({ role })
            });
            return handleResponse(res);
        },
        uploadVerification: async (aadhar, degree, skillCertificate) => {
            const formData = new FormData();
            if (aadhar) formData.append('aadhar', aadhar);
            if (degree) formData.append('degree', degree);
            if (skillCertificate) formData.append('skill_certificate', skillCertificate);
            
            const res = await fetch(`${API_BASE}/users/verify/upload`, {
                method: 'PUT',
                headers: authHeader(),
                body: formData
            });
            return handleResponse(res);
        },
        approveVerification: async (userId) => {
            const res = await fetch(`${API_BASE}/users/${userId}/verify/approve`, {
                method: 'PUT',
                headers: authHeader()
            });
            return handleResponse(res);
        },
        rejectVerification: async (userId) => {
            const res = await fetch(`${API_BASE}/users/${userId}/verify/reject`, {
                method: 'PUT',
                headers: authHeader()
            });
            return handleResponse(res);
        },
        delete: async (userId) => {
            const res = await fetch(`${API_BASE}/users/${userId}`, {
                method: 'DELETE',
                headers: authHeader()
            });
            return handleResponse(res);
        }
    },
    courses: {
        getAll: async () => {
            const res = await fetch(`${API_BASE}/courses/`);
            return handleResponse(res);
        },
        getMyCreated: async () => {
            const res = await fetch(`${API_BASE}/courses/my_created`, { headers: authHeader() });
            return handleResponse(res);
        },
        getOne: async (id) => {
            const res = await fetch(`${API_BASE}/courses/${id}`);
            return handleResponse(res);
        },
        create: async (courseData) => {
            const res = await fetch(`${API_BASE}/courses/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify(courseData)
            });
            return handleResponse(res);
        },
        delete: async (id) => {
            const res = await fetch(`${API_BASE}/courses/${id}`, {
                method: 'DELETE',
                headers: authHeader()
            });
            return handleResponse(res);
        }
    },
    bookings: {
        create: async (courseId) => {
            const res = await fetch(`${API_BASE}/bookings/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify({ course_id: parseInt(courseId) })
            });
            return handleResponse(res);
        },
        getMy: async () => {
            const res = await fetch(`${API_BASE}/bookings/my_bookings`, { headers: authHeader() });
            return handleResponse(res);
        },
        getAll: async () => {
            const res = await fetch(`${API_BASE}/bookings/all`, { headers: authHeader() });
            return handleResponse(res);
        }
    },
    materials: {
        getForCourse: async (courseId) => {
            const res = await fetch(`${API_BASE}/materials/course/${courseId}`, { headers: authHeader() });
            return handleResponse(res);
        },
        upload: async (courseId, title, file) => {
            const formData = new FormData();
            formData.append('course_id', courseId);
            formData.append('title', title);
            formData.append('file', file);
            
            const res = await fetch(`${API_BASE}/materials/`, {
                method: 'POST',
                headers: authHeader(),
                body: formData
            });
            return handleResponse(res);
        }
    },
    assignments: {
        getForCourse: async (courseId) => {
            const res = await fetch(`${API_BASE}/assignments/course/${courseId}`, { headers: authHeader() });
            return handleResponse(res);
        },
        create: async (courseId, title, description, dueDate, file) => {
            const formData = new FormData();
            formData.append('course_id', courseId);
            formData.append('title', title);
            formData.append('description', description);
            if (dueDate) formData.append('due_date', dueDate);
            if (file) formData.append('file', file);
            
            const res = await fetch(`${API_BASE}/assignments/`, {
                method: 'POST',
                headers: authHeader(),
                body: formData
            });
            return handleResponse(res);
        },
        delete: async (id) => {
            // Future implementation if needed
            throw new Error("Not implemented");
        }
    },
    submissions: {
        getForAssignment: async (assignmentId) => {
            const res = await fetch(`${API_BASE}/submissions/assignment/${assignmentId}`, { headers: authHeader() });
            return handleResponse(res);
        },
        create: async (assignmentId, file) => {
            const formData = new FormData();
            formData.append('file', file);
            
            const res = await fetch(`${API_BASE}/submissions/assignment/${assignmentId}`, {
                method: 'POST',
                headers: authHeader(),
                body: formData
            });
            return handleResponse(res);
        },
        grade: async (submissionId, grade, feedback) => {
            const res = await fetch(`${API_BASE}/submissions/${submissionId}/grade?grade=${encodeURIComponent(grade)}&feedback=${encodeURIComponent(feedback)}`, {
                method: 'PUT',
                headers: authHeader()
            });
            return handleResponse(res);
        }
    },
    payments: {
        enroll: async (bookingId, amount) => {
            const res = await fetch(`${API_BASE}/payments/enroll`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify({ booking_id: parseInt(bookingId), amount: parseFloat(amount) })
            });
            return handleResponse(res);
        },
        getRevenue: async () => {
            const res = await fetch(`${API_BASE}/payments/admin/revenue`, { headers: authHeader() });
            return handleResponse(res);
        },
        getSalaries: async () => {
            const res = await fetch(`${API_BASE}/payments/admin/salaries`, { headers: authHeader() });
            return handleResponse(res);
        },
        payTutor: async (tutorId, courseId, amount) => {
            const res = await fetch(`${API_BASE}/payments/admin/pay_tutor`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify({ tutor_id: parseInt(tutorId), course_id: parseInt(courseId), amount: parseFloat(amount) })
            });
            return handleResponse(res);
        }
    }
};
