const { createApp } = Vue;

createApp({
    data() {
        return {
            lots: [],
            newLot: {
                name: '',
                address: '',
                pin_code: '',
                price: '',
                total_spots: ''
            },
            message: ''
        }
    },
    methods: {
        async fetchLots() {
            const token = localStorage.getItem('token');
            const role = localStorage.getItem('role');

            if (!token || role !== 'admin') {
                alert('Access denied!');
                window.location.href = 'index.html';
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/admin/lots', {
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
                    this.lots = data.lots;
                } else {
                    alert('Failed to load lots');
                }
            } catch (error) {
                console.error('Error fetching lots:', error);
            }
        },

        async addLot() {
            const token = localStorage.getItem('token');

            if (!this.newLot.name || !this.newLot.address || !this.newLot.price || !this.newLot.total_spots) {
                this.message = 'Please fill all required fields!';
                return;
            }

            const lotData = {
                name: this.newLot.name.trim(),
                address: this.newLot.address.trim(),
                pin_code: this.newLot.pin_code.trim(),
                price: parseFloat(this.newLot.price),
                total_spots: parseInt(this.newLot.total_spots)
            };

            try {
                const response = await fetch('http://127.0.0.1:5000/admin/lots', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(lotData),
                    credentials: 'include',
                    mode: 'cors'
                });

                const data = await response.json();
                this.message = data.message || 'Something went wrong';

                if (response.ok) {
                    this.newLot = { name: '', address: '', pin_code: '', price: '', total_spots: '' };
                    this.fetchLots();
                } else {
                    console.error('Server Error:', data);
                }
            } catch (error) {
                console.error('Error adding lot:', error);
                this.message = 'Network error while adding lot';
            }
        },

        async updateLot(lot) {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`http://127.0.0.1:5000/admin/lots/${lot.id}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(lot),
                    credentials: 'include',
                    mode: 'cors'
                });

                const data = await response.json();
                this.message = data.message || 'Update failed';
            } catch (error) {
                console.error('Error updating lot:', error);
            }
        },

        async deleteLot(lotId) {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`http://127.0.0.1:5000/admin/lots/${lotId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` },
                    credentials: 'include', 
                    mode: 'cors'
                });

                const data = await response.json();
                this.message = data.message || 'Failed to delete lot';
                if (response.ok) this.fetchLots();
            } catch (error) {
                console.error('Error deleting lot:', error);
            }
        },

        goBack() {
            window.location.href = 'admin_dashboard.html';
        },

        logout() {
            localStorage.clear();
            window.location.href = 'index.html';
        }
    },

    mounted() {
        this.fetchLots();
    }
}).mount('#lotManagementApp');
