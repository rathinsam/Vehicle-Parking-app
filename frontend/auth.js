const { createApp } = Vue;

//Login App
if (document.querySelector('#loginApp')) {
    createApp({
        data() {
            return {
                username: '',
                password: '',
                errorMessage: ''
            }
        },
        methods: {
            async loginUser() {
                if (!this.username || !this.password) {
                    this.errorMessage = "Please fill all fields!";
                    return;
                }

                try {
                    const response = await fetch('http://127.0.0.1:5000/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: this.username,
                            password: this.password
                        }),
                        credentials: 'include',
                        mode: 'cors'
                    });

                    const data = await response.json();

                    if (response.ok) {
                        localStorage.setItem('token', data.token);
                        localStorage.setItem('role', data.role);
                        localStorage.setItem('username', data.username);

                        if (data.role === 'admin') {
                            window.location.href = 'admin_dashboard.html';
                        } else {
                            window.location.href = 'user_dashboard.html';
                        }
                    } else {
                        this.errorMessage = data.message || 'Login failed';
                    }
                } catch (error) {
                    this.errorMessage = 'Error connecting to server';
                }
            }
        }
    }).mount('#loginApp');
}

//Register App
if (document.querySelector('#registerApp')) {
    createApp({
        data() {
            return {
                username: '',
                password: '',
                errorMessage: '',
                successMessage: ''
            }
        },
        methods: {
            async registerUser() {
                if (!this.username || !this.password) {
                    this.errorMessage = "Please fill all fields!";
                    return;
                }

                try {
                    const response = await fetch('http://127.0.0.1:5000/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: this.username,
                            password: this.password
                        }),
                        credentials: 'include',
                        mode: 'cors'
                    });

                    const data = await response.json();

                    if (response.ok) {
                        this.successMessage = data.message;
                        this.errorMessage = '';
                        this.username = '';
                        this.password = '';
                    } else {
                        this.errorMessage = data.message || 'Registration failed';
                        this.successMessage = '';
                    }
                } catch (error) {
                    this.errorMessage = 'Error connecting to server';
                }
            }
        }
    }).mount('#registerApp');
}

