const { createApp } = Vue;

createApp({
    data() {
        return {
            summary: {
                total_reservations: 0,
                total_amount_spent: 0,
                active_reservations: null,
                recent_history: [],
                reservations_per_lot: {},
                spending_trend: {}
            },
            chartsInitialized: false,
            lotChartInstance: null,
            spendingChartInstance: null
        }
    },
    methods: {
        async fetchDashboard() {
            const token = localStorage.getItem('token');
            const role = localStorage.getItem('role');

            if (!token || role !== 'user') {
                alert('Access denied!');
                window.location.href = 'index.html';
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/user/dashboard', {
                    headers: { 'Authorization': `Bearer ${token}` },
                    credentials: 'include',
                    mode: 'cors'
                });

                if (response.ok) {
                    const data = await response.json();
                    this.summary = data;

                    // After getting data, update charts
                    this.initCharts();
                } else {
                    // alert('Failed to load user dashboard');
                    alert('Session Expired! Failed to load user dashboard');
                    this.logout()
                }
            } catch (error) {
                console.error('Error fetching user dashboard:', error);
            }
        },
        async releaseSpot() {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch('http://127.0.0.1:5000/user/release', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    credentials: 'include',
                    mode: 'cors'
                });

                const data = await response.json();
                if (response.ok) {
                    alert(`Spot released! Cost: ₹${data.cost}`);
                    this.fetchDashboard();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error('Error releasing spot:', error);
            }
        },
        logout() {
            localStorage.clear();
            window.location.href = 'index.html';
        },
        goToReservePage() {
            window.location.href = 'reserve.html';
        },
        formatDate(dateString) {
            if (!dateString) return '-';
            return new Date(dateString).toLocaleString();
        },
        initCharts() {
            const token = localStorage.getItem('token');

            fetch('http://127.0.0.1:5000/user/reservations', {
                headers: { 'Authorization': `Bearer ${token}` },
                credentials: 'include',
                mode: 'cors'
            })
                .then(response => response.json())
                .then(data => {
                    const fullHistory = data.history;  // Full reservations data
                    const lots = {};
                    const monthlySpending = {};

                    fullHistory.forEach(r => {
                        // Count reservations per lot
                        lots[r.lot_name] = (lots[r.lot_name] || 0) + 1;

                        // Sum monthly spending
                        if (r.parking_time && r.cost) {
                            const month = new Date(r.parking_time).toLocaleString('default', { month: 'short' });
                            monthlySpending[month] = (monthlySpending[month] || 0) + r.cost;
                        }
                    });

                    //Reservations per Lot
                    const lotCtx = document.getElementById('lotChart').getContext('2d');
                    new Chart(lotCtx, {
                        type: 'bar',
                        data: {
                            labels: Object.keys(lots),
                            datasets: [{
                                label: 'Reservations',
                                data: Object.values(lots),
                                backgroundColor: '#36a2eb'
                            }]
                        }
                    });

                    //Spending Trend
                    const spendingCtx = document.getElementById('spendingChart').getContext('2d');
                    new Chart(spendingCtx, {
                        type: 'line',
                        data: {
                            labels: Object.keys(monthlySpending),
                            datasets: [{
                                label: 'Amount Spent (₹)',
                                data: Object.values(monthlySpending),
                                borderColor: '#4bc0c0',
                                fill: false
                            }]
                        }
                    });
                })
                .catch(error => {
                    console.error('Error fetching full reservation history:', error);
                });
        }

    },
    mounted() {
        this.fetchDashboard();
    }
}).mount('#userDashboardApp');
