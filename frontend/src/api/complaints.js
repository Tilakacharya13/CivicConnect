import api from './client'

export const getMyComplaints = () => api.get('/complaints/my').then(response => response.data)
export const getComplaint = id => api.get(`/complaints/${id}`).then(response => response.data)
export const getTimeline = id => api.get(`/complaints/${id}/timeline`).then(response => response.data)
export const createComplaint = body => api.post('/complaints', body).then(response => response.data)
export const uploadBeforePhoto = (id, file) => { const form = new FormData(); form.append('file', file); return api.post(`/complaints/${id}/photo`, form).then(response => response.data) }
export const submitFeedback = (id, body) => api.post(`/complaints/${id}/feedback`, body).then(response => response.data)
export const getQueue = () => api.get('/admin/queue').then(response => response.data)
export const getAdminComplaints = params => api.get('/admin/complaints', { params }).then(response => response.data)
export const getAdminStats = () => api.get('/admin/stats').then(response => response.data)
export const getOverdue = () => api.get('/admin/overdue').then(response => response.data)
export const updateComplaintStatus = (id, body) => api.patch(`/admin/complaints/${id}/status`, body).then(response => response.data)
export const uploadAfterPhoto = (id, file) => { const form = new FormData(); form.append('file', file); return api.post(`/admin/complaints/${id}/after-photo`, form).then(response => response.data) }
export const recalculate = () => api.post('/admin/recalculate').then(response => response.data)
