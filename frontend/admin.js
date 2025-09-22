const { createApp } = Vue;

createApp({
    data() {
        return {
            summary: {
                total_lots: 0,
                total_spots: 0,
                available_spots: 0,
                occupied_spots: 0,
                total_users: 0,
                total_revenue: 0,
                lots: []
            },
            reservations: [],
            allReservations: [],
            cards: [],
            chartsInitialized: false
        }
    },
    methods: {
        async fetchDashboard() {
            const token = localStorage.getItem('token');
            const role = localStorage.getItem('role');

            if (!token || role !== 'admin') {
                alert('Access denied!');
                window.location.href = 'index.html';
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/admin/dashboard', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include', 
                    mode: 'cors' 
                });


                if (response.ok) {
                    const data = await response.json();
                    this.summary = data;
                    this.reservations = data.reservations;

                    this.cards = [
                        { title: 'Total Lots', value: data.total_lots },
                        { title: 'Total Spots', value: data.total_spots },
                        { title: 'Available', value: data.available_spots },
                        { title: 'Occupied', value: data.occupied_spots },
                        { title: 'Total Users', value: data.total_users },
                        { title: 'Revenue (₹)', value: (data.total_revenue || 0).toFixed(2) }
                    ];

                    if (!this.chartsInitialized) {
                        this.initCharts();
                        this.chartsInitialized = true;
                    }
                } else {
                    alert('Failed to load dashboard data');
                    this.logout()
                }
            } catch (error) {
                console.error('Error fetching dashboard:', error);
            }
        },
        async fetchAllReservations() {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch('http://127.0.0.1:5000/admin/reservations', {
                    headers: { 'Authorization': `Bearer ${token}` },
                    credentials: 'include',
                    mode: 'cors'
                });
                if (response.ok) {
                    const data = await response.json();
                    this.allReservations = data.reservations;
                }
            } catch (error) {
                console.error('Error fetching all reservations:', error);
            }
        },
        initCharts() {
            const ctx1 = document.getElementById('spotsPieChart');
            new Chart(ctx1, {
                type: 'pie',
                data: {
                    labels: ['Available', 'Occupied'],
                    datasets: [{
                        data: [this.summary.available_spots, this.summary.occupied_spots],
                    }]
                }
            });

            const ctx2 = document.getElementById('lotsBarChart');
            const labels = this.summary.lots.map(lot => lot.name);
            const occupiedData = this.summary.lots.map(lot => lot.occupied);

            // alert(labels)
            // alert(occupiedData)

            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Occupied Spots',
                        data: occupiedData,
                        backgroundcolor: '#61c28cff'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });




        },


        logout() {
            localStorage.clear();
            window.location.href = 'index.html';
        },
        goToLotManagement() {
            window.location.href = 'admin_lots.html';
        },
        formatDate(dateString) {
            if (!dateString) return '-';
            return new Date(dateString).toLocaleString();
        }
    },
    mounted() {
        this.fetchDashboard();
        this.fetchAllReservations();
    }
}).mount('#adminDashboardApp');

