const { createApp } = Vue;

createApp({
    data() {
        return {
            reservations: []
        };
    },
    methods: {
        async fetchHistory() {
            const token = localStorage.getItem('token');
            const role = localStorage.getItem('role');

            if (!token || role !== 'user') {
                alert('Access denied!');
                window.location.href = 'index.html';
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/user/reservations', {
                    headers: { 'Authorization': `Bearer ${token}` },
                    credentials: 'include',
                    mode: 'cors'
                });
                if (response.ok) {
                    const data = await response.json();
                    this.reservations = data.history || [];
                } else {
                    console.error('Failed to fetch history:', await response.text());
                }
            } catch (error) {
                console.error('Error fetching history:', error);
            }
        },
        logout() {
            localStorage.clear();
            window.location.href = 'index.html';
        },
        goBack() {
            window.location.href = 'user_dashboard.html';
        },
        formatDate(dateString) {
            return new Date(dateString).toLocaleString();
        }
    },
    mounted() {
        this.fetchHistory();
    }
}).mount('#historyApp');



document.getElementById('exportBtn').addEventListener('click', async () => {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('http://127.0.0.1:5000/user/export', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            credentials: 'include',
            mode: 'cors'
        });
        const data = await response.json();
        alert(data.message);
    } catch (error) {
        alert('Error exporting CSV');
    }
});