        // Update time every second
        setInterval(() => {
            const now = new Date();
            document.getElementById('currentTime').innerText = now.toLocaleString('en-IN', {
                weekday: 'short', year: 'numeric', month: 'short',
                day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
        }, 1000);

        // Demo fallback data shown when backend is unavailable
        const DEMO_EMPLOYEES = [
            { employee_id: 1, name: "Amit Kumar",    designation: "Helper",     basic_salary: 18000, is_active: true },
            { employee_id: 2, name: "Priya Singh",   designation: "Supervisor", basic_salary: 35000, is_active: true },
            { employee_id: 3, name: "Rajesh Sharma", designation: "Technician", basic_salary: 27000, is_active: true },
            { employee_id: 4, name: "Sunita Verma",  designation: "Operator",   basic_salary: 22000, is_active: true },
            { employee_id: 5, name: "Vijay Yadav",   designation: "Helper",     basic_salary: 16000, is_active: true },
            { employee_id: 6, name: "Anjali Gupta",  designation: "Manager",    basic_salary: 45000, is_active: true },
            { employee_id: 7, name: "Suresh Raina",  designation: "Security",   basic_salary: 14000, is_active: true },
            { employee_id: 8, name: "Meena Kumari",  designation: "Helper",     basic_salary: 15000, is_active: true },
        ];

        const today = new Date().toISOString().split('T')[0];
        const DEMO_ATTENDANCE = DEMO_EMPLOYEES.map((emp, i) => ({
            employee_id: emp.employee_id,
            name: emp.name,
            designation: emp.designation,
            remarks: emp.designation,
            status: ['P','P','P','A','HD','P','P','CL'][i] || 'P',
            in_time: ['08:55','09:05','08:48','--:--','09:30','08:52','09:15','--:--'][i] || '09:00',
            out_time: ['18:02','18:10','17:55','--:--','14:00','18:05','18:20','--:--'][i] || '18:00',
            is_late: [false, true, false, false, false, false, true, false][i] || false,
            date: today
        }));

        // Fetch dashboard stats — returns a Promise
        async function fetchStats() {
            const API_BASE = 'http://localhost:5000/api';
            
            try {
                const [empRes, attRes] = await Promise.all([
                    fetch(`${API_BASE}/employees/`),
                    fetch(`${API_BASE}/attendance/list/${today}`)
                ]);

                if (!empRes.ok || !attRes.ok) throw new Error('API server error');

                const emps = await empRes.json();
                const atts = await attRes.json();

                renderDashboard(emps, atts);
            } catch (err) {
                console.warn("Backend unavailable, showing demo data:", err.message);
                renderDashboard(DEMO_EMPLOYEES, DEMO_ATTENDANCE);
                showDemoWarning();
            }
        }

        function showDemoWarning() {
            let banner = document.getElementById('demoBanner');
            if (!banner) {
                banner = document.createElement('div');
                banner.id = 'demoBanner';
                banner.style.cssText = `
                    position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
                    background: rgba(245,158,11,0.95); color: white; padding: 0.6rem 1.4rem;
                    border-radius: 12px; font-weight: 700; font-size: 0.88rem;
                    z-index: 9999; box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                    display: flex; align-items: center; gap: 0.5rem;
                `;
                banner.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Backend offline — showing demo data';
                document.body.appendChild(banner);
                setTimeout(() => banner.remove(), 5000);
            }
        }

        function renderDashboard(emps, atts) {
            document.getElementById('totalEmpCount').innerText = emps.length;

            const presentCount = atts.filter(a => a.status === 'P' || a.status === 'HD').length;
            const late = atts.filter(a => a.is_late).length;
            const percent = emps.length > 0 ? Math.round((presentCount / emps.length) * 100) : 0;

            document.getElementById('todayPresentPercent').innerText = `${percent}%`;
            document.getElementById('todayLateCount').innerText = late;

            // Sort: Present first, then by employee_id
            const statusVal = { 'P': 1, 'HD': 2, 'CL': 3, 'SL': 4, 'A': 5 };
            const sortedLogs = [...atts].sort((x, y) => {
                const sx = statusVal[x.status] || 99;
                const sy = statusVal[y.status] || 99;
                if (sx !== sy) return sx - sy;
                return x.employee_id - y.employee_id;
            });

            const tbody = document.querySelector('#recentLogTable tbody');
            if (sortedLogs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-dim);">No attendance records for today.</td></tr>`;
                return;
            }

            tbody.innerHTML = sortedLogs.map(a => `
                <tr>
                    <td style="font-weight:600;">${a.name || '-'}</td>
                    <td style="color:var(--text-dim);">${a.remarks || a.designation || '-'}</td>
                    <td class="status-${(a.status || 'a').toLowerCase()}">${a.status || '-'}</td>
                    <td>${a.in_time || '--:--'} ${a.is_late ? '<span class="status-late">LATE</span>' : ''}</td>
                    <td>${a.out_time || '--:--'}</td>
                </tr>
            `).join('');
        }

        fetchStats();
