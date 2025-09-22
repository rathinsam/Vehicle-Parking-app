const { createApp } = Vue;

createApp({
    data() {
        return {
            lots: [],
            activeReservation: null,
            message: "",
        };
    },
    methods: {
        async fetchLots() {
            const token = localStorage.getItem("token");
            const role = localStorage.getItem("role");
            if (!token || role !== "user") {
                alert("Access denied!");
                window.location.href = "index.html";
                return;
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/user/lots", {
                    headers: { Authorization: `Bearer ${token}` },
                    credentials: 'include',
                    mode: 'cors'
                });
                if (response.ok) {
                    const data = await response.json();
                    this.lots = data.lots; // Directly use backend response
                }
            } catch (error) {
                console.error("Error fetching lots:", error);
                this.message = "Error loading lots";
            }
        },
        async fetchActiveReservation() {
            const token = localStorage.getItem("token");
            try {
                const response = await fetch("http://127.0.0.1:5000/user/dashboard", {
                    headers: { Authorization: `Bearer ${token}` },
                    credentials: 'include',
                    mode: 'cors'
                });
                if (response.ok) {
                    const data = await response.json();
                    if (data.active_reservations) {
                        this.activeReservation = {
                            lot_name: data.active_reservations.lot_name,
                            spot_id: data.active_reservations.spot_id,
                            parked_since: data.active_reservations.parked_since,
                        };
                    } else {
                        this.activeReservation = null;
                    }
                }
            } catch (error) {
                console.error("Error fetching active reservation:", error);
                this.message = "Error loading active reservation";
            }
        },
        async reserveLot(lotId) {
            const token = localStorage.getItem("token");
            try {
                const response = await fetch(
                    `http://127.0.0.1:5000/user/reserve/${lotId}`,
                    {
                        method: "POST",
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                        credentials: 'include',
                        mode: 'cors'
                    }
                );
                const data = await response.json();
                if (response.ok) {
                    this.message = `Reservation successful! Spot ID: ${data.spot_id}`;
                    this.fetchLots();
                    this.fetchActiveReservation();
                } else {
                    this.message = data.message || "Failed to reserve spot";
                }
                setTimeout(() => (this.message = ""), 3000);
            } catch (error) {
                console.error("Error reserving lot:", error);
                this.message = "Error reserving spot";
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
                    this.message = `Spot released! Cost ₹${data.cost}`;
                    alert(this.message);
                    this.activeReservation = null;
                    this.fetchLots();
                } else {
                    this.message = data.message || "Failed to release spot";
                }
                setTimeout(() => this.message = '', 3000);
            } catch (error) {
                console.error('Error releasing spot:', error);
                this.message = 'Error releasing spot';
            }
        },
        logout() {
            localStorage.clear();
            window.location.href = "index.html";
        },
        goBack() {
            window.location.href = "user_dashboard.html";
        },
        formatDate(dateString) {
            return new Date(dateString).toLocaleString();
        },
    },
    mounted() {
        this.fetchLots();
        this.fetchActiveReservation();
    },
}).mount("#reserveApp");
